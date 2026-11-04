"""Parse the sniffer's text output into validated TECH bus frames.

The sniffer prints one line per frame: "45DE U1 (20): 0226 FFFA 0405 0000 0218 A5F3".
U1 is the boiler, U2 the modules replying to it.

A frame is made of big-endian 16-bit words:

    0226  address  (param value)...  0218  crc
"""

import re
from collections import namedtuple

FRAME_START = 0x0226
FRAME_END = 0x0218

# These params say which valve or room unit the following values belong to.
# They are stored as context on each value, not as values themselves.
SELECTOR_PARAMS = {0x16F9, 0x16EF}

# Multi-word blocks with their own length field. Not seen on the EL-480 so far,
# and reading them as param/value pairs would store wrong data.
BLOCK_PARAMS = {0x1788, 0x0400}

LINE_RE = re.compile(r"[0-9A-F]{4} (U[12]) \((\d+)\):((?: [0-9A-F]{1,4})*)")

Value = namedtuple("Value", "selector param value")
Frame = namedtuple("Frame", "source address values")


class FrameError(Exception):
    """A line that isn't a valid frame. str(error) is the reason, used in stats."""


def crc16(data):
    """CRC over the bytes before the end marker: start FFFF, reflected poly 8408."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8408 if crc & 1 else crc >> 1
    return crc


def parse_line(line):
    """Return the Frame on a sniffer line, or raise FrameError."""
    match = LINE_RE.fullmatch(line.strip())
    if match is None:
        raise FrameError("unparsed")

    source, count, hex_groups = match.groups()
    hex_text = hex_groups.replace(" ", "")
    if len(hex_text) % 2 or len(hex_text) // 2 != int(count):
        raise FrameError("bad_length")
    data = bytes.fromhex(hex_text)

    # Modules end each reply with one extra 00, outside the CRC. It is probably
    # the sender releasing the line, seen by the UART as a break.
    if len(data) % 2 and data[-1] == 0:
        data = data[:-1]
    if len(data) % 2 or len(data) < 8:
        raise FrameError("bad_shape")

    words = [int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2)]
    body = words[2:-2]
    if words[0] != FRAME_START or words[-2] != FRAME_END or len(body) % 2:
        raise FrameError("bad_shape")
    if crc16(data[:-4]) != words[-1]:
        raise FrameError("bad_crc")

    return Frame(source, words[1], _decode_body(body))


def _decode_body(body):
    values = []
    selector = 0
    for i in range(0, len(body), 2):
        param, value = body[i], body[i + 1]
        if param in BLOCK_PARAMS:
            raise FrameError("block")
        if param in SELECTOR_PARAMS:
            selector = value
        else:
            values.append(Value(selector, param, value))
    return values
