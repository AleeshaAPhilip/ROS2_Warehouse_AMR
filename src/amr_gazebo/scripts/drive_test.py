#!/usr/bin/env python3
"""Drive test: `drive_test.py straight` (2 m) or `drive_test.py spin` (360 deg)."""
import sys, math, rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

mode = sys.argv[1] if len(sys.argv) > 1 else 'straight'
lin, ang, dur = (0.2, 0.0, 10.0) if mode == 'straight' else (0.0, 0.5, 2 * math.pi / 0.5)

rclpy.init()
n = Node('drive_test', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
pub = n.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)
odom = {}
n.create_subscription(Odometry, '/diff_drive_controller/odom', lambda m: odom.update(last=m), 10)

def pose():
    p = odom['last'].pose.pose
    return p.position.x, p.position.y, 2 * math.atan2(p.orientation.z, p.orientation.w)

def send(v, w):
    m = TwistStamped()
    m.header.stamp = n.get_clock().now().to_msg()
    m.header.frame_id = 'base_link'
    m.twist.linear.x, m.twist.angular.z = v, w
    pub.publish(m)

while 'last' not in odom or n.get_clock().now().nanoseconds == 0:   # wait for sim clock + odom
    rclpy.spin_once(n, timeout_sec=0.1)
x0, y0, yaw0 = pose()
t0 = n.get_clock().now()
print(f'Running "{mode}" for {dur:.1f} sim-seconds ...')
while (n.get_clock().now() - t0).nanoseconds * 1e-9 < dur:
    send(lin, ang)
    rclpy.spin_once(n, timeout_sec=0.05)
for _ in range(10):
    send(0.0, 0.0)
    rclpy.spin_once(n, timeout_sec=0.05)
rclpy.spin_once(n, timeout_sec=0.5)
x1, y1, yaw1 = pose()
dyaw = math.degrees(math.atan2(math.sin(yaw1 - yaw0), math.cos(yaw1 - yaw0)))
print(f'distance moved: {math.hypot(x1 - x0, y1 - y0):.3f} m   (dx={x1 - x0:.3f}, dy={y1 - y0:.3f})')
print(f'heading change (wrapped): {dyaw:.1f} deg')
rclpy.shutdown()
