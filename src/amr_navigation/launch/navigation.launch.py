import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    nav_share = get_package_share_directory('amr_navigation')
    bringup = get_package_share_directory('nav2_bringup')
    params = os.path.join(nav_share, 'config', 'nav2_params.yaml')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(bringup, 'launch', 'navigation_launch.py')),
        launch_arguments={'use_sim_time': 'true', 'params_file': params, 'autostart': 'true'}.items())

    # Nav2 publishes Twist on /cmd_vel; diff_drive_controller expects TwistStamped
    stamper = Node(package='twist_stamper', executable='twist_stamper', name='twist_stamper',
                   parameters=[{'use_sim_time': True, 'frame_id': 'base_link'}],
                   remappings=[('cmd_vel_in', '/cmd_vel'),
                               ('cmd_vel_out', '/diff_drive_controller/cmd_vel')])

    return LaunchDescription([nav2, stamper])
