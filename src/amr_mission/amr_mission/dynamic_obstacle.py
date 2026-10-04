#!/usr/bin/env python3
"""Paces the Gazebo 'walker' box back and forth across the central aisle."""
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class Walker(Node):
    def __init__(self):
        super().__init__('dynamic_obstacle')
        self.declare_parameter('speed', 0.25)
        self.declare_parameter('half_period', 8.0)
        self.speed = float(self.get_parameter('speed').value)
        self.half = float(self.get_parameter('half_period').value)
        self.pub = self.create_publisher(Twist, '/walker/cmd_vel', 10)
        self.t0 = self.get_clock().now()
        self.create_timer(0.1, self.tick)

    def tick(self):
        t = (self.get_clock().now() - self.t0).nanoseconds * 1e-9
        direction = 1.0 if int(t // self.half) % 2 == 0 else -1.0
        msg = Twist()
        msg.linear.y = direction * self.speed
        self.pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(Walker())
    rclpy.shutdown()


if __name__ == '__main__':
    main()
