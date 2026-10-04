#!/usr/bin/env python3
"""Drive, then compare raw odom / EKF / ground truth.  Usage: drive_compare.py straight|spin"""
import sys, math, rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

mode = sys.argv[1] if len(sys.argv) > 1 else 'straight'
lin, ang, dur = (0.2, 0.0, 10.0) if mode == 'straight' else (0.0, 0.5, 2 * math.pi / 0.5)
TOPICS = {'raw odom': '/diff_drive_controller/odom', 'EKF': '/odometry/filtered',
          'truth': '/ground_truth/odom'}

rclpy.init()
n = Node('drive_compare', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
pub = n.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)
last = {}
for name, topic in TOPICS.items():
    n.create_subscription(Odometry, topic, lambda m, k=name: last.__setitem__(k, m), 10)

def pose(k):
    p = last[k].pose.pose
    return p.position.x, p.position.y, 2 * math.atan2(p.orientation.z, p.orientation.w)

def send(v, w):
    m = TwistStamped()
    m.header.stamp = n.get_clock().now().to_msg()
    m.header.frame_id = 'base_link'
    m.twist.linear.x, m.twist.angular.z = v, w
    pub.publish(m)

while len(last) < len(TOPICS) or n.get_clock().now().nanoseconds == 0:
    rclpy.spin_once(n, timeout_sec=0.1)
start = {k: pose(k) for k in TOPICS}
t0 = n.get_clock().now()
print(f'Running "{mode}" for {dur:.1f} sim-seconds ...')
while (n.get_clock().now() - t0).nanoseconds * 1e-9 < dur:
    send(lin, ang)
    rclpy.spin_once(n, timeout_sec=0.05)
for _ in range(20):
    send(0.0, 0.0)
    rclpy.spin_once(n, timeout_sec=0.05)
rclpy.spin_once(n, timeout_sec=0.5)

print(f'{"source":10s} {"distance (m)":>13s} {"heading change (deg)":>22s}')
for k in TOPICS:
    x0, y0, a0 = start[k]
    x1, y1, a1 = pose(k)
    da = math.degrees(math.atan2(math.sin(a1 - a0), math.cos(a1 - a0)))
    print(f'{k:10s} {math.hypot(x1 - x0, y1 - y0):13.3f} {da:22.1f}')
rclpy.shutdown()
