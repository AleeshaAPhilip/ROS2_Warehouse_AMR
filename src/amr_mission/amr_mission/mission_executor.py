#!/usr/bin/env python3
"""Run a named-location mission with Nav2: HOME -> Shelf A -> Shelf B -> Charging Station."""
import csv
import math
import os
import time
from datetime import datetime

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from lifecycle_msgs.srv import GetState
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.parameter import Parameter


def make_pose(nav, x, y, yaw):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.z = math.sin(yaw / 2.0)
    pose.pose.orientation.w = math.cos(yaw / 2.0)
    return pose


def wait_active(nav, node_name):
    client = nav.create_client(GetState, f'/{node_name}/get_state')
    while not client.wait_for_service(timeout_sec=1.0):
        nav.get_logger().info(f'waiting for /{node_name} ...')
    while rclpy.ok():
        future = client.call_async(GetState.Request())
        rclpy.spin_until_future_complete(nav, future, timeout_sec=2.0)
        if future.done() and future.result().current_state.label == 'active':
            return
        time.sleep(1.0)


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
    default_file = os.path.join(get_package_share_directory('amr_mission'), 'config', 'locations.yaml')
    nav.declare_parameter('locations_file', default_file)
    nav.declare_parameter('route', ['shelf_a', 'shelf_b', 'charging_station'])
    nav.declare_parameter('retries', 3)
    nav.declare_parameter('log_file', os.path.expanduser('~/amr_ws/docs/mission_runs.csv'))

    log = nav.get_logger()
    with open(nav.get_parameter('locations_file').value) as f:
        locs = yaml.safe_load(f)
    route = list(nav.get_parameter('route').value)
    retries = int(nav.get_parameter('retries').value)

    wait_active(nav, 'amcl')
    wait_active(nav, 'bt_navigator')
    log.info(f'Mission start. Route: HOME -> ' + ' -> '.join(route))

    while nav.get_clock().now().nanoseconds == 0:   # wait for the first /clock message
        rclpy.spin_once(nav, timeout_sec=0.1)
    t_start = nav.get_clock().now()
    total_retries = 0
    failed_at = ''
    try:
        for name in route:
            if name not in locs:
                log.error(f'Unknown location "{name}"')
                failed_at = name
                break
            reached = False
            for attempt in range(1, retries + 1):
                log.info(f'--> {name} (attempt {attempt}/{retries})')
                nav.goToPose(make_pose(nav, **locs[name]))
                last_print = 0.0
                while not nav.isTaskComplete():
                    fb = nav.getFeedback()
                    if fb and time.time() - last_print > 3.0:
                        log.info(f'    {name}: {fb.distance_remaining:.1f} m remaining')
                        last_print = time.time()
                if nav.getResult() == TaskResult.SUCCEEDED:
                    log.info(f'Reached {name}')
                    reached = True
                    break
                total_retries += 1
                log.warn(f'{name}: attempt {attempt} failed, clearing costmaps and retrying')
                nav.clearAllCostmaps()
                time.sleep(1.0)
            if not reached:
                failed_at = name
                break
            if name == 'charging_station':
                log.info('Docked. Charging ...')
                time.sleep(3.0)
    except KeyboardInterrupt:
        nav.cancelTask()
        failed_at = 'interrupted'

    elapsed = (nav.get_clock().now() - t_start).nanoseconds * 1e-9
    success = failed_at == ''
    log.info(f'Mission {"COMPLETE" if success else "FAILED at " + failed_at} '
             f'in {elapsed:.0f} sim-seconds ({total_retries} retries)')

    path = nav.get_parameter('log_file').value
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new_file = not os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(['timestamp', 'success', 'sim_seconds', 'retries', 'failed_at'])
        w.writerow([datetime.now().isoformat(timespec='seconds'), int(success),
                    f'{elapsed:.1f}', total_retries, failed_at])

    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
