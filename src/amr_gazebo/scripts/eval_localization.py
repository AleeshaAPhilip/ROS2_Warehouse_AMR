#!/usr/bin/env python3
"""Closed-loop 2.5 x 1.5 m clockwise rectangle from HOME.
Legs use heading hold + EKF distance; corners turn to an EKF heading target.
Compares raw odom / EKF / AMCL against Gazebo ground truth."""
import math, rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import TwistStamped, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry

HOME_X, HOME_Y = -6.0, 0.0      # HOME in Gazebo world coordinates = origin of the saved map
LEGS = [2.5, 1.5, 2.5, 1.5]     # metres, clockwise
V = 0.2                          # m/s

rclpy.init()
n = Node('eval_localization', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
pub = n.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)
last = {}

def as_tuple(p):
    return p.position.x, p.position.y, 2 * math.atan2(p.orientation.z, p.orientation.w)

for key, topic in {'raw odom': '/diff_drive_controller/odom', 'EKF': '/odometry/filtered',
                   'truth': '/ground_truth/odom'}.items():
    n.create_subscription(Odometry, topic,
                          lambda m, k=key: last.__setitem__(k, as_tuple(m.pose.pose)), 10)
n.create_subscription(PoseWithCovarianceStamped, '/amcl_pose',
                      lambda m: last.__setitem__('AMCL', as_tuple(m.pose.pose)), 10)

pos_err = {k: [] for k in ('raw odom', 'EKF', 'AMCL')}
yaw_err = {k: [] for k in pos_err}
now_s = lambda: n.get_clock().now().nanoseconds * 1e-9
wrap = lambda a: math.atan2(math.sin(a), math.cos(a))
clamp = lambda x, lo, hi: max(lo, min(hi, x))
state = {'next': 0.0}

def send(v, w):
    m = TwistStamped()
    m.header.stamp = n.get_clock().now().to_msg()
    m.header.frame_id = 'base_link'
    m.twist.linear.x, m.twist.angular.z = v, w
    pub.publish(m)

def sample():
    tx, ty, ta = last['truth'][0] - HOME_X, last['truth'][1] - HOME_Y, last['truth'][2]
    for k in pos_err:
        if k in last:
            x, y, a = last[k]
            pos_err[k].append(math.hypot(x - tx, y - ty))
            yaw_err[k].append(abs(math.degrees(wrap(a - ta))))

def tick(v, w):
    send(v, w)
    rclpy.spin_once(n, timeout_sec=0.05)
    if now_s() >= state['next']:
        sample()
        state['next'] = now_s() + 0.2

def pause(secs):
    t0 = now_s()
    while now_s() - t0 < secs:
        tick(0.0, 0.0)

def drive_leg(length, heading):
    x0, y0, _ = last['EKF']
    t0 = now_s()
    while now_s() - t0 < 60.0:
        x, y, a = last['EKF']
        if math.hypot(x - x0, y - y0) >= length:
            break
        tick(V, clamp(2.0 * wrap(heading - a), -0.3, 0.3))
    pause(0.7)

def turn_to(heading):
    t0 = now_s()
    while now_s() - t0 < 30.0:
        err = wrap(heading - last['EKF'][2])
        if abs(err) < 0.015:
            break
        w = clamp(1.5 * abs(err), 0.08, 0.4) * (1 if err > 0 else -1)
        tick(0.0, w)
    pause(0.7)

while not all(k in last for k in ('raw odom', 'EKF', 'truth')) or now_s() == 0:
    rclpy.spin_once(n, timeout_sec=0.1)
yaw0 = last['EKF'][2]
print('Driving the rectangle (closed-loop, about 1-2 sim-minutes) ...')
for i, length in enumerate(LEGS):
    drive_leg(length, yaw0 - i * math.pi / 2)
    turn_to(yaw0 - (i + 1) * math.pi / 2)
pause(1.0)
sample()

print(f'\n{"source":10s} {"mean pos err (m)":>17s} {"max (m)":>9s} {"final (m)":>10s} {"mean yaw err (deg)":>19s}')
for k in pos_err:
    if pos_err[k]:
        e, y = pos_err[k], yaw_err[k]
        print(f'{k:10s} {sum(e)/len(e):17.3f} {max(e):9.3f} {e[-1]:10.3f} {sum(y)/len(y):19.1f}')
    else:
        print(f'{k:10s} no data (is localization running?)')
rclpy.shutdown()
