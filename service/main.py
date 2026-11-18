#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "eclipse-zenoh==1.10.2",
#     "pycdr2==1.0.0",
# ]
# ///
"""Increment the int received on <input_prefix>/input and publish it on <output_prefix>/output.

When nothing arrives on the input for 5 seconds, publish 0 instead.
Each message is a CDR encoded int32, the same layout as std_msgs/msg/Int32.
"""

# Without it, pycdr2 1.0.0 sees no fields in Message on Python 3.14
from __future__ import annotations

import argparse
import logging
import queue
from dataclasses import dataclass

import zenoh
from pycdr2 import IdlStruct
from pycdr2.types import int32

TIMEOUT = 5

logger = logging.getLogger(__name__)


@dataclass
class Message(IdlStruct):
    counter: int32


def main(input_prefix: str, output_prefix: str) -> None:
    samples: queue.Queue[zenoh.Sample] = queue.Queue()
    with zenoh.open(zenoh.Config()) as session:
        publisher = session.declare_publisher(f"{output_prefix}/output")
        session.declare_subscriber(f"{input_prefix}/input", samples.put)
        while True:
            try:
                sample = samples.get(timeout=TIMEOUT)
                message = Message.deserialize(sample.payload.to_bytes())
                payload = Message(message.counter + 1).serialize()
            except queue.Empty:
                payload = Message(0).serialize()
            except Exception as exception:  # noqa: BLE001 pycdr2 raises a bare Exception on overflow
                logger.warning(f"Ignoring invalid message: {exception}")
                continue
            publisher.put(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_prefix", help="prefix of the input key, like service1")
    parser.add_argument("output_prefix", help="prefix of the output key, like service2")
    args = parser.parse_args()
    main(args.input_prefix, args.output_prefix)
