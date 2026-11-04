#!/usr/bin/env python3
"""Publish selected boiler values to MQTT, with Home Assistant discovery.

Runs beside the reader in its own thread. MQTT problems are logged and retried,
and never stop the reader or the web page.

The connection settings come from a TOML file kept out of git:

    host = "192.168.1.x"
    port = 1883
    username = "kotelna"
    password = "..."

Run "mqtt_pub.py --remove" to delete the entities from Home Assistant.
"""

import argparse
import json
import logging
import os
import threading
import time

from params import MQTT_ENTITIES
from web import STALE_SECONDS, pick_reading

BASE_TOPIC = "kotelna"
AVAILABILITY_TOPIC = f"{BASE_TOPIC}/availability"
DISCOVERY_PREFIX = "homeassistant"
HA_STATUS_TOPIC = f"{DISCOVERY_PREFIX}/status"
PUBLISH_INTERVAL = 5.0

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mqtt.toml")
DEVICE = {
    "identifiers": ["kotelna"],
    "name": "Kotelna",
    "manufacturer": "TECH / Elektromet",
    "model": "EL-480",
}

log = logging.getLogger("mqtt")


def state_topic(entity):
    return f"{BASE_TOPIC}/{entity.key}"


def discovery_topic(entity):
    return f"{DISCOVERY_PREFIX}/{entity.component}/kotelna/{entity.key}/config"


def discovery_payload(entity):
    return {
        "name": entity.name,
        "unique_id": f"kotelna_{entity.key}",
        "state_topic": state_topic(entity),
        "availability_topic": AVAILABILITY_TOPIC,
        "device": DEVICE,
        **entity.extras,
    }


class MqttPublisher:
    def __init__(self, store, client, interval=PUBLISH_INTERVAL):
        self.store = store
        self.client = client
        self.interval = interval
        self.sent = {}
        self.availability = None
        self.needs_full_publish = False
        self.stop_event = threading.Event()
        self.thread = None
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            log.warning("connection refused: %s", reason_code)
            return
        log.info("connected")
        client.subscribe(HA_STATUS_TOPIC)
        self.needs_full_publish = True

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        log.warning("disconnected: %s", reason_code)

    def on_message(self, client, userdata, message):
        # Home Assistant announces its restarts here, so tell it about us again.
        if message.topic == HA_STATUS_TOPIC and message.payload == b"online":
            self.needs_full_publish = True

    def publish_once(self, now):
        if not self.client.is_connected():
            return

        if self.needs_full_publish:
            self.needs_full_publish = False
            self.sent.clear()
            self.availability = None
            for entity in MQTT_ENTITIES:
                self.client.publish(discovery_topic(entity),
                                    json.dumps(discovery_payload(entity)), qos=1, retain=True)

        values, _, last_frame = self.store.snapshot()

        online = last_frame is not None and now - last_frame <= STALE_SECONDS
        availability = "online" if online else "offline"
        if availability != self.availability:
            self.client.publish(AVAILABILITY_TOPIC, availability, qos=1, retain=True)
            self.availability = availability
        if not online:
            return

        for entity in MQTT_ENTITIES:
            entry = pick_reading(values, entity.selector, entity.param, now)
            if entry is None:
                continue
            payload = str(entity.convert(entry[0]))
            if self.sent.get(entity.key) != payload:
                self.client.publish(state_topic(entity), payload, retain=True)
                self.sent[entity.key] = payload

    def run(self):
        while not self.stop_event.wait(self.interval):
            try:
                self.publish_once(time.time())
            except Exception:
                log.exception("publish failed")

    def start(self):
        self.client.will_set(AVAILABILITY_TOPIC, "offline", qos=1, retain=True)
        self.client.loop_start()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=5)
        if self.client.is_connected():
            info = self.client.publish(AVAILABILITY_TOPIC, "offline", qos=1, retain=True)
            info.wait_for_publish(timeout=2)
        self.client.disconnect()
        self.client.loop_stop()


def load_config(path):
    import tomllib  # needs Python 3.11, and only the Pi runs this

    with open(path, "rb") as file:
        return tomllib.load(file)


def create_client(config):
    import paho.mqtt.client as mqtt

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="kotelna-reader")
    client.username_pw_set(config["username"], config["password"])
    client.reconnect_delay_set(min_delay=1, max_delay=60)
    return client


def start_mqtt(store, config_path):
    """Start publishing if configured. Returns the publisher, or None."""
    if not os.path.exists(config_path):
        log.info("no %s, MQTT is off", config_path)
        return None
    try:
        config = load_config(config_path)
        client = create_client(config)
        publisher = MqttPublisher(store, client)
        # connect_async also retries if the broker is down when we start.
        client.connect_async(config["host"], config.get("port", 1883))
        publisher.start()
    except Exception:
        log.exception("MQTT is off, can't start it")
        return None
    log.info("publishing to %s:%s", config["host"], config.get("port", 1883))
    return publisher


def remove_entities(config_path):
    config = load_config(config_path)
    client = create_client(config)
    client.connect(config["host"], config.get("port", 1883))
    client.loop_start()
    topics = [discovery_topic(entity) for entity in MQTT_ENTITIES]
    topics += [state_topic(entity) for entity in MQTT_ENTITIES]
    topics.append(AVAILABILITY_TOPIC)
    for topic in topics:
        client.publish(topic, b"", qos=1, retain=True).wait_for_publish(timeout=5)
    client.disconnect()
    client.loop_stop()
    print(f"cleared {len(topics)} retained topics")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--remove", action="store_true", help="delete the HA entities and exit")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    if args.remove:
        remove_entities(args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
