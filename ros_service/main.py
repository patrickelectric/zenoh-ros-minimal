#!/usr/bin/env python3
"""Increment the message received on <input_prefix>/input and publish it on <output_prefix>/output.

Every number in it goes up by 1 and wraps around at the end of its range, so a byte at 255 becomes 0.
An empty string becomes "potato" and "potato" becomes "chips".
Each reply goes out 500 ms after its input, so two services feeding each other don't spin.
When nothing arrives on the input for 5 seconds, publish zeros and an empty string instead.
This is service/main.py over ROS 2 topics, with ros_zenoh_msgs/msg/Message messages.
"""

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
