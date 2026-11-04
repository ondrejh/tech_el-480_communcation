"""Read-only local web page and JSON API for the live values."""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from params import PARAM_NAMES, PREFERRED_ADDRESSES, READINGS, signed

PAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

# A value not refreshed for this long is treated as out of date.
STALE_SECONDS = 30


def pick_reading(values, selector, param, now):
    """Return the boiler's value from the preferred address that's still fresh."""
    found = [values.get(("U1", address, selector, param)) for address in PREFERRED_ADDRESSES]
    found = [entry for entry in found if entry is not None]
    for entry in found:
        if now - entry[2] <= STALE_SECONDS:
            return entry
    return found[0] if found else None


def build_payload(store, now):
    values, totals, last_frame = store.snapshot()

    readings = []
    for reading in READINGS:
        entry = pick_reading(values, reading.selector, reading.param, now)
        readings.append({
            "group": reading.group,
            "label": reading.label,
            "text": reading.format(entry[0]) if entry else None,
            "age": now - entry[2] if entry else None,
        })

    raw = [{
        "source": source,
        "address": f"{address:04X}",
        "selector": selector,
        "param": f"{param:04X}",
        "name": PARAM_NAMES.get(param, ""),
        "value": entry[0],
        "hex": f"{entry[0]:04X}",
        "signed": signed(entry[0]),
        "age": now - entry[2],
        "changed_ago": now - entry[3],
    } for (source, address, selector, param), entry in sorted(values.items())]

    return {
        "last_frame_age": now - last_frame if last_frame else None,
        "stale_seconds": STALE_SECONDS,
        "totals": totals,
        "readings": readings,
        "raw": raw,
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            with open(PAGE_PATH, "rb") as page:
                self.respond(page.read(), "text/html; charset=utf-8")
        elif path == "/api/values":
            payload = build_payload(self.server.store, time.time())
            self.respond(json.dumps(payload).encode(), "application/json")
        else:
            self.send_error(404)

    def respond(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # one line every few seconds per open page would only fill the log


def start_web_server(store, port, host="0.0.0.0"):
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.store = store
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
