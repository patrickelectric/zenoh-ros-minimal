#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "eclipse-zenoh==1.10.2",
#     "pycdr2==1.0.0",
# ]
# ///
"""Increment the message received on <input_prefix>/input and publish it on <output_prefix>/output."""

# Without it, pycdr2 1.0.0 sees no fields in Message on Python 3.14
from __future__ import annotations

import argparse
import builtins
import ctypes
import logging
import queue
import struct
import time
from dataclasses import dataclass

import zenoh
from pycdr2 import IdlStruct
from pycdr2.types import int32, int64, uint8, uint16

TIMEOUT = 5
DELAY = 0.5

logger = logging.getLogger(__name__)


@dataclass
class Message(IdlStruct):
    counter: int32 = 0
    byte1: uint8 = 0
    byte2: uint8 = 0
    counter2: int64 = 0
    # pycdr2 resolves annotation names in this module only, so builtins need their module path
    message: builtins.str = ""
    counter3: uint16 = 0


def main(input_prefix: str, output_prefix: str) -> None:
    samples: queue.Queue[zenoh.Sample] = queue.Queue()
    with zenoh.open(zenoh.Config()) as session:
        publisher = session.declare_publisher(f"{output_prefix}/output")
        session.declare_subscriber(f"{input_prefix}/input", samples.put)
        while True:
            try:
                sample = samples.get(timeout=TIMEOUT)
                received = Message.deserialize(sample.payload.to_bytes())
                logger.info(f"Received {received}")
                payload = Message(
                    counter=ctypes.c_int32(received.counter + 1).value,
                    byte1=ctypes.c_uint8(received.byte1 + 1).value,
                    byte2=ctypes.c_uint8(received.byte2 + 1).value,
                    counter2=ctypes.c_int64(received.counter2 + 1).value,
                    message=received.message.replace("potato", "chips") or "potato",
                    counter3=ctypes.c_uint16(received.counter3 + 1).value,
                ).serialize()
                time.sleep(DELAY)
            except queue.Empty:
                payload = Message().serialize()
            except (struct.error, UnicodeDecodeError) as exception:
                logger.warning(f"Ignoring invalid message: {exception}")
                continue
            publisher.put(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_prefix", help="prefix of the input key, like service1")
    parser.add_argument("output_prefix", help="prefix of the output key, like service2")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    main(args.input_prefix, args.output_prefix)
