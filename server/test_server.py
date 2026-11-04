#!/usr/bin/env python3
import os
import tempfile
import unittest

import json
import urllib.error
import urllib.request

import params
from protocol import Frame, FrameError, Value, crc16, parse_line
from store import Store
from mqtt_pub import (AVAILABILITY_TOPIC, HA_STATUS_TOPIC, MqttPublisher,
                      discovery_payload, discovery_topic, state_topic)
from reader import handle_line
from web import STALE_SECONDS, build_payload, pick_reading, start_web_server

TESTFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "listener", "testfile.txt")

# Captured live from the EL-480 on 2026-11-04.
LIVE_U1 = "45DE U1 (20): 0226 FFFA 0405 0000 0406 0000 0404 0000 0218 A5F3"
LIVE_U2 = "6D61 U2 (17): 0226 0000 0405 00C8 0406 0000 0218 D978 00"
LIVE_SELECTOR = ("6D2E U1 (44): 0226 FFF4 16F9 0001 1699 00F8 1581 0001 169A 00C8 178C 1E05 "
                 "178D 00C8 178E 0000 0405 0000 16F9 0000 0218 4A48")


class ProtocolTest(unittest.TestCase):
    def assert_rejected(self, line, expected):
        with self.assertRaises(FrameError) as caught:
            parse_line(line)
        self.assertEqual(str(caught.exception), expected)

    def test_crc_of_empty_frame(self):
        self.assertEqual(crc16(bytes.fromhex("0226FFF4")), 0xA1DE)

    def test_boiler_frame(self):
        frame = parse_line(LIVE_U1)
        self.assertEqual(frame.source, "U1")
        self.assertEqual(frame.address, 0xFFFA)
        self.assertEqual(frame.values[0], Value(0, 0x0405, 0))

    def test_module_frame_with_trailing_zero(self):
        frame = parse_line(LIVE_U2)
        self.assertEqual(frame, Frame("U2", 0, [Value(0, 0x0405, 200), Value(0, 0x0406, 0)]))

    def test_selector_applies_to_following_values(self):
        values = parse_line(LIVE_SELECTOR).values
        self.assertIn(Value(1, 0x1699, 248), values)
        self.assertTrue(all(v.param != 0x16F9 for v in values))

    def test_selector_resets_for_values_after_it(self):
        crc = crc16(bytes.fromhex("0226FFF416F90001167F002E16F90000157D0226"))
        frame = parse_line(f"0000 U1 (24): 0226 FFF4 16F9 0001 167F 002E 16F9 0000 "
                           f"157D 0226 0218 {crc:04X}")
        self.assertEqual(frame.values, [Value(1, 0x167F, 46), Value(0, 0x157D, 550)])

    def test_all_2017_boiler_frames_pass_and_garbled_replies_fail(self):
        results = {"U1": [0, 0], "U2": [0, 0]}
        with open(TESTFILE, errors="replace") as lines:
            for line in lines:
                source = "U1" if " U1 " in line else "U2" if " U2 " in line else None
                if source is None:
                    continue
                try:
                    parse_line(line)
                    results[source][0] += 1
                except FrameError:
                    results[source][1] += 1
        self.assertEqual(results["U1"], [332, 0])
        self.assertEqual(results["U2"], [0, 332])

    def test_rejects_changed_data(self):
        self.assert_rejected(LIVE_U1.replace("0404 0000", "0404 0001"), "bad_crc")

    def test_rejects_wrong_byte_count(self):
        self.assert_rejected(LIVE_U1.replace("(20)", "(22)"), "bad_length")

    def test_rejects_cut_off_line(self):
        self.assert_rejected("0226 FFFA 0405", "unparsed")

    def test_rejects_wrong_start(self):
        self.assert_rejected("0000 U1 (8): 0227 FFF4 0218 A1DE", "bad_shape")

    def test_rejects_block_frames(self):
        crc = crc16(bytes.fromhex("0226FFF417880001"))
        self.assert_rejected(f"0000 U1 (12): 0226 FFF4 1788 0001 0218 {crc:04X}", "block")


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "test.db")
        self.store = Store(self.path)

    def tearDown(self):
        self.store.db.close()
        self.dir.cleanup()

    def frame(self, value):
        return Frame("U1", 0xFFF4, [Value(0, 0x157D, value)])

    def rows(self, sql):
        return self.store.db.execute(sql).fetchall()

    def test_history_only_records_changes(self):
        self.store.record_frame(self.frame(500), 100.0)
        self.store.record_frame(self.frame(500), 110.0)
        self.store.record_frame(self.frame(510), 120.0)
        self.store.flush()
        self.assertEqual(self.rows("SELECT ts, value FROM value_changes ORDER BY ts"),
                         [(100.0, 500), (120.0, 510)])
        self.assertEqual(
            self.rows("SELECT value, first_seen, last_seen, last_changed FROM current_values"),
            [(510, 100.0, 120.0, 120.0)])

    def test_restart_does_not_repeat_unchanged_values(self):
        self.store.record_frame(self.frame(500), 100.0)
        self.store.close()
        self.store = Store(self.path)
        self.store.record_frame(self.frame(500), 200.0)
        self.store.flush()
        self.assertEqual(self.rows("SELECT COUNT(*) FROM value_changes"), [(1,)])
        self.assertEqual(self.rows("SELECT last_seen FROM current_values"), [(200.0,)])

    def test_same_param_is_separate_per_selector_and_source(self):
        self.store.record_frame(Frame("U1", 1, [Value(1, 5, 10), Value(2, 5, 20)]), 1.0)
        self.store.record_frame(Frame("U2", 1, [Value(1, 5, 30)]), 1.0)
        self.store.flush()
        self.assertEqual(self.rows("SELECT COUNT(*) FROM current_values"), [(3,)])

    def test_stats_add_up_across_flushes(self):
        self.store.count("bad_crc", 3700.0)
        self.store.flush()
        self.store.count("bad_crc", 3710.0)
        self.store.flush()
        self.assertEqual(self.rows("SELECT hour, kind, count FROM reader_stats"),
                         [(3600, "bad_crc", 2)])


class FormatTest(unittest.TestCase):
    def test_temperatures(self):
        self.assertEqual(params.temp_tenths(0x0226), "55.0 °C")
        self.assertEqual(params.temp_tenths(0xFFFB), "-0.5 °C")

    def test_captured_values(self):
        self.assertEqual(params.clock(0x1334), "19:52")
        self.assertEqual(params.min_max(0x502D), "45–80 °C")
        self.assertEqual(params.fuel_level(0x2C00), "22 %")
        self.assertEqual(params.weekday(3), "Wednesday")

    def test_unknown_codes_stay_visible(self):
        self.assertEqual(params.state(0x09), "0x09")
        self.assertEqual(params.pump_mode(9), "9")


class WebTest(unittest.TestCase):
    NOW = 1000.0

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.store = Store(os.path.join(self.dir.name, "test.db"))

    def tearDown(self):
        self.store.db.close()
        self.dir.cleanup()

    def add(self, address, value, ts=NOW):
        self.store.record_frame(Frame("U1", address, [Value(0, 0x157D, value)]), ts)

    def boiler_reading(self, payload):
        return next(r for r in payload["readings"]
                    if r["group"] == "Boiler" and r["label"] == "Temperature")

    def test_prefers_fff4(self):
        self.add(0xFFFA, 500)
        self.add(0xFFF4, 510)
        payload = build_payload(self.store, self.NOW)
        self.assertEqual(self.boiler_reading(payload)["text"], "51.0 °C")

    def test_falls_back_when_fff4_is_stale(self):
        self.add(0xFFF4, 510, self.NOW - STALE_SECONDS - 1)
        self.add(0xFFFA, 500)
        values = self.store.snapshot()[0]
        self.assertEqual(pick_reading(values, 0, 0x157D, self.NOW)[0], 500)

    def test_module_values_are_not_used_as_boiler_readings(self):
        self.store.record_frame(Frame("U2", 0xFFF4, [Value(0, 0x157D, 999)]), self.NOW)
        self.assertIsNone(self.boiler_reading(build_payload(self.store, self.NOW))["text"])

    def test_payload_marks_age_and_keeps_unnamed_values(self):
        self.store.record_frame(Frame("U1", 0xFFF4, [Value(0, 0x1581, 1)]), self.NOW - 5)
        payload = build_payload(self.store, self.NOW)
        self.assertEqual(payload["last_frame_age"], 5)
        self.assertEqual(payload["raw"][0]["param"], "1581")
        self.assertEqual(payload["raw"][0]["name"], "")

    def test_no_data_yet(self):
        payload = build_payload(self.store, self.NOW)
        self.assertIsNone(payload["last_frame_age"])
        self.assertTrue(all(r["text"] is None for r in payload["readings"]))

    def test_http_routes(self):
        self.add(0xFFF4, 510)
        server = start_web_server(self.store, 0, "127.0.0.1")
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/") as response:
                self.assertIn(b"Kotelna", response.read())
            with urllib.request.urlopen(base + "/api/values") as response:
                self.assertEqual(json.load(response)["raw"][0]["value"], 510)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(base + "/../reader.py")
            self.assertEqual(caught.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()


class RejectTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.store = Store(os.path.join(self.dir.name, "test.db"))

    def tearDown(self):
        self.store.db.close()
        self.dir.cleanup()

    def test_rejected_lines_are_kept_for_diagnosis(self):
        handle_line(self.store, b"0000 U1 (8): 0227 FFF4 0218 A1DE\r")
        handle_line(self.store, b"\xff\xfe garbage")
        self.assertEqual(self.store.totals, {"bad_shape": 1, "unparsed": 1})
        self.assertEqual([r["kind"] for r in self.store.recent_rejects], ["bad_shape", "unparsed"])
        self.assertIn("0227", self.store.recent_rejects[0]["line"])

    def test_good_lines_are_not_rejects(self):
        handle_line(self.store, LIVE_U1.encode() + b"\r")
        self.assertEqual(len(self.store.recent_rejects), 0)
        self.assertEqual(self.store.totals, {"ok_U1": 1})


class FakeClient:
    def __init__(self):
        self.connected = True
        self.published = []
        self.subscribed = []

    def is_connected(self):
        return self.connected

    def publish(self, topic, payload, qos=0, retain=False):
        self.published.append((topic, payload, retain))

    def subscribe(self, topic):
        self.subscribed.append(topic)


class FakeReason:
    is_failure = False


class FakeMessage:
    topic = HA_STATUS_TOPIC
    payload = b"online"


class MqttTest(unittest.TestCase):
    NOW = 1000.0
    BOILER = next(e for e in params.MQTT_ENTITIES if e.key == "boiler_temperature")

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.store = Store(os.path.join(self.dir.name, "test.db"))
        self.client = FakeClient()
        self.publisher = MqttPublisher(self.store, self.client)
        self.publisher.on_connect(self.client, None, None, FakeReason(), None)

    def tearDown(self):
        self.store.db.close()
        self.dir.cleanup()

    def add(self, value, ts=NOW):
        self.store.record_frame(Frame("U1", 0xFFF4, [Value(0, 0x157D, value)]), ts)

    def states(self):
        return [p for p in self.client.published if p[0] == state_topic(self.BOILER)]

    def test_discovery_is_retained_and_describes_entity(self):
        self.publisher.publish_once(self.NOW)
        topic = discovery_topic(self.BOILER)
        self.assertEqual(topic, "homeassistant/sensor/kotelna/boiler_temperature/config")
        message = next(p for p in self.client.published if p[0] == topic)
        self.assertTrue(message[2])
        config = json.loads(message[1])
        self.assertEqual(config["unit_of_measurement"], "°C")
        self.assertEqual(config["availability_topic"], AVAILABILITY_TOPIC)
        self.assertEqual(config["device"]["name"], "Kotelna")

    def test_unique_ids_are_unique(self):
        ids = [discovery_payload(e)["unique_id"] for e in params.MQTT_ENTITIES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_values_publish_only_when_changed(self):
        self.add(540)
        self.publisher.publish_once(self.NOW)
        self.add(540)
        self.publisher.publish_once(self.NOW)
        self.add(550)
        self.publisher.publish_once(self.NOW)
        self.assertEqual([s[1] for s in self.states()], ["54.0", "55.0"])

    def test_goes_offline_when_boiler_data_stops(self):
        self.add(540)
        self.publisher.publish_once(self.NOW)
        self.publisher.publish_once(self.NOW + STALE_SECONDS + 1)
        availability = [p[1] for p in self.client.published if p[0] == AVAILABILITY_TOPIC]
        self.assertEqual(availability, ["online", "offline"])

    def test_stays_offline_with_no_data_at_all(self):
        self.publisher.publish_once(self.NOW)
        self.assertEqual([p[1] for p in self.client.published if p[0] == AVAILABILITY_TOPIC],
                         ["offline"])
        self.assertEqual(self.states(), [])

    def test_publishes_nothing_while_disconnected(self):
        self.add(540)
        self.client.connected = False
        self.publisher.publish_once(self.NOW)
        self.assertEqual(self.client.published, [])

    def test_home_assistant_restart_resends_everything(self):
        self.add(540)
        self.publisher.publish_once(self.NOW)
        self.client.published.clear()
        self.publisher.on_message(self.client, None, FakeMessage())
        self.publisher.publish_once(self.NOW)
        self.assertEqual(len(self.states()), 1)
        self.assertTrue(any(p[0] == discovery_topic(self.BOILER) for p in self.client.published))

    def test_reconnect_subscribes_to_home_assistant_status(self):
        self.assertEqual(self.client.subscribed, [HA_STATUS_TOPIC])

    def test_binary_and_negative_payloads(self):
        self.assertEqual(params.binary_payload(1), "ON")
        self.assertEqual(params.binary_payload(0), "OFF")
        self.assertEqual(params.tenths_number(0xFFFB), -0.5)
        self.assertEqual(params.fuel_percent(0x2C00), 22)


if __name__ == "__main__":
    unittest.main()
