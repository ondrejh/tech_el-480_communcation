#!/usr/bin/env python3
"""Read the sniffer's serial output and store validated values in SQLite."""

import argparse
import fcntl
import logging
import os
import select
import signal
import termios
import time
import tty

from protocol import FrameError, parse_line
from store import Store

MAX_LINE_BYTES = 8192
RECONNECT_SECONDS = 5

log = logging.getLogger("reader")


def open_port(device):
    # O_NOCTTY matters: without it this process can take the port as its
    # controlling terminal and get stopped when reading it in the background.
    fd = os.open(device, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    # Refuse other non-root readers, which would silently split the data with us.
    fcntl.ioctl(fd, termios.TIOCEXCL)
    tty.setraw(fd)
    attrs = termios.tcgetattr(fd)
    attrs[2] |= termios.CLOCAL | termios.CREAD
    attrs[4] = attrs[5] = termios.B115200
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return fd


def handle_line(store, line):
    now = time.time()
    try:
        store.record_frame(parse_line(line.decode("ascii")), now)
    except UnicodeDecodeError:
        store.count("unparsed", now)
    except FrameError as error:
        store.count(str(error), now)


def read_port(fd, store, flush_interval, should_stop):
    """Read until asked to stop, or raise OSError if the port goes away."""
    buffer = b""
    synced = False  # the first line after opening is usually cut off
    next_flush = time.monotonic() + flush_interval

    while not should_stop():
        ready, _, _ = select.select([fd], [], [], 1.0)
        if ready:
            data = os.read(fd, 4096)
            if not data:
                raise OSError("serial port closed")
            *lines, buffer = (buffer + data).split(b"\n")
            for line in lines:
                if synced:
                    handle_line(store, line)
                synced = True
            if len(buffer) > MAX_LINE_BYTES:
                store.count("unparsed", time.time())
                buffer = b""

        if time.monotonic() >= next_flush:
            store.flush()
            next_flush = time.monotonic() + flush_interval


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="/dev/ttyACM0")
    parser.add_argument("--db", default="kotelna.db")
    parser.add_argument("--flush-interval", type=float, default=60.0,
                        help="seconds between database writes")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    stop = []
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.append(True))

    store = Store(args.db)
    try:
        while not stop:
            try:
                fd = open_port(args.device)
            except OSError as error:
                log.warning("cannot open %s: %s", args.device, error)
                time.sleep(RECONNECT_SECONDS)
                continue
            log.info("reading %s", args.device)
            try:
                read_port(fd, store, args.flush_interval, lambda: stop)
            except OSError as error:
                log.warning("lost %s: %s", args.device, error)
            finally:
                os.close(fd)
    finally:
        store.close()
        log.info("stopped")


if __name__ == "__main__":
    main()
