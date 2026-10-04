import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

# HOME pad position in the Gazebo world
HOME_X, HOME_Y, HOME_YAW = -6.0, 0.0, 0.0


def generate_launch_description():
    desc = get_package_share_directory('amr_description')
    gz = get_package_share_directory('amr_gazebo')
    ros_gz = get_package_share_directory('ros_gz_sim')

    robot_description = ParameterValue(
        Command(['xacro ', os.path.join(desc, 'urdf', 'amr.urdf.xacro')]), value_type=str)

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ', os.path.join(gz, 'worlds') + '/', LaunchConfiguration('world')],
                          'on_exit_shutdown': 'true'}.items())

    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description, 'use_sim_time': True}])

    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-topic', 'robot_description', '-name', 'amr',
                            '-x', str(HOME_X), '-y', str(HOME_Y), '-z', '0.1', '-Y', str(HOME_YAW)])

    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  parameters=[{'config_file': os.path.join(gz, 'config', 'bridge.yaml')}])

    jsb = Node(package='controller_manager', executable='spawner',
               arguments=['joint_state_broadcaster', '--controller-manager-timeout', '30'])
    ddc = Node(package='controller_manager', executable='spawner',
               arguments=['diff_drive_controller', '--controller-manager-timeout', '30'])

    # use sim.rviz once you've saved it (Part G), otherwise open RViz with defaults
    rviz_cfg = os.path.join(desc, 'rviz', 'sim.rviz')
    rviz = Node(package='rviz2', executable='rviz2',
                arguments=['-d', rviz_cfg] if os.path.exists(rviz_cfg) else [],
                parameters=[{'use_sim_time': True}])

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='warehouse.sdf'),
        gz_sim, rsp, spawn, bridge,
        RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=[jsb])),
        RegisterEventHandler(OnProcessExit(target_action=jsb, on_exit=[ddc])),
        rviz,
    ])
