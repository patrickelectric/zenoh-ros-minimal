#!/usr/bin/env python3
"""Increment the message received on <input_prefix>/input and publish it on <output_prefix>/output."""

import argparse
import ctypes
import time

import rclpy
from rclpy.utilities import remove_ros_args
from ros_zenoh_msgs.msg import Message

TIMEOUT = 5
DELAY = 0.5


def main(input_prefix: str, output_prefix: str) -> None:
    rclpy.init()
    node = rclpy.create_node("service")
    publisher = node.create_publisher(Message, f"{output_prefix}/output", 10)
    timer = node.create_timer(TIMEOUT, lambda: publisher.publish(Message()))

    def on_input(received: Message) -> None:
        node.get_logger().info(f"Received {received}")
        time.sleep(DELAY)
        timer.reset()
        publisher.publish(
            Message(
                counter=ctypes.c_int32(received.counter + 1).value,
                byte1=ctypes.c_uint8(received.byte1 + 1).value,
                byte2=ctypes.c_uint8(received.byte2 + 1).value,
                counter2=ctypes.c_int64(received.counter2 + 1).value,
                message=received.message.replace("potato", "chips") or "potato",
                counter3=ctypes.c_uint16(received.counter3 + 1).value,
            )
        )

    node.create_subscription(Message, f"{input_prefix}/input", on_input, 10)
    rclpy.spin(node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_prefix", help="prefix of the input topic, like service1")
    parser.add_argument("output_prefix", help="prefix of the output topic, like service2")
    args = parser.parse_args(remove_ros_args()[1:])
    main(args.input_prefix, args.output_prefix)
