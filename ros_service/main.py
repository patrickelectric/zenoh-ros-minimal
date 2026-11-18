#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.14.*"
# dependencies = [
#     "ros-kilted-rclpy[fastrtps]==9.1.2",
#     "ros-kilted-std-msgs==5.5.1",
# ]
# ///
"""Increment the int received on <input_prefix>/input and publish it on <output_prefix>/output.

When nothing arrives on the input for 5 seconds, publish 0 instead.
This is service/main.py over ROS 2 topics, with std_msgs/msg/Int32 messages.
"""

import argparse

import rclpy
from rclpy.utilities import remove_ros_args
from std_msgs.msg import Int32

TIMEOUT = 5
INT32_MAX = 2**31 - 1


def main(input_prefix: str, output_prefix: str) -> None:
    rclpy.init()
    node = rclpy.create_node("service")
    publisher = node.create_publisher(Int32, f"{output_prefix}/output", 10)
    timer = node.create_timer(TIMEOUT, lambda: publisher.publish(Int32(data=0)))

    def on_input(message: Int32) -> None:
        node.get_logger().info(f"Received {message.data}")
        timer.reset()
        if message.data == INT32_MAX:
            node.get_logger().warning(f"Ignoring {message.data}, it overflows int32 when incremented")
            return
        publisher.publish(Int32(data=message.data + 1))

    node.create_subscription(Int32, f"{input_prefix}/input", on_input, 10)
    rclpy.spin(node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_prefix", help="prefix of the input topic, like service1")
    parser.add_argument("output_prefix", help="prefix of the output topic, like service2")
    args = parser.parse_args(remove_ros_args()[1:])
    main(args.input_prefix, args.output_prefix)
