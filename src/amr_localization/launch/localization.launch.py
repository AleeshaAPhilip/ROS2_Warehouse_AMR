import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    loc = get_package_share_directory('amr_localization')
    nav = get_package_share_directory('amr_navigation')
    default_map = os.path.join(nav, 'maps', 'warehouse.yaml')

    map_arg = DeclareLaunchArgument('map', default_value=default_map)

    ekf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(loc, 'launch', 'ekf.launch.py')))

    map_server = Node(package='nav2_map_server', executable='map_server', name='map_server',
                      output='screen',
                      parameters=[{'use_sim_time': True, 'yaml_filename': LaunchConfiguration('map')}])

    amcl = Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen',
                parameters=[os.path.join(loc, 'config', 'amcl.yaml')])

    lifecycle = Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
                     name='lifecycle_manager_localization', output='screen',
                     parameters=[{'use_sim_time': True, 'autostart': True,
                                  'node_names': ['map_server', 'amcl']}])

    return LaunchDescription([map_arg, ekf, map_server, amcl, lifecycle])
