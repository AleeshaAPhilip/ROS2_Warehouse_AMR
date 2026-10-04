import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def include(pkg, name, args=None):
    path = os.path.join(get_package_share_directory(pkg), 'launch', name)
    return IncludeLaunchDescription(PythonLaunchDescriptionSource(path),
                                    launch_arguments=(args or {}).items())


def generate_launch_description():
    dynamic = LaunchConfiguration('dynamic')
    mission = LaunchConfiguration('mission')
    world = PythonExpression(["'warehouse_dynamic.sdf' if '", dynamic, "' == 'true' else 'warehouse.sdf'"])

    sim = include('amr_gazebo', 'sim.launch.py', {'world': world})
    localization = TimerAction(period=30.0, actions=[include('amr_localization', 'localization.launch.py')])
    navigation = TimerAction(period=55.0, actions=[include('amr_navigation', 'navigation.launch.py')])
    walker = TimerAction(period=55.0, actions=[
        Node(package='amr_mission', executable='dynamic_obstacle', output='screen',
             parameters=[{'use_sim_time': True}], condition=IfCondition(dynamic))])
    mission_node = TimerAction(period=90.0, actions=[
        Node(package='amr_mission', executable='mission_executor', output='screen',
             parameters=[{'use_sim_time': True}], condition=IfCondition(mission))])

    return LaunchDescription([
        DeclareLaunchArgument('dynamic', default_value='false',
                              description='true = warehouse with a moving obstacle'),
        DeclareLaunchArgument('mission', default_value='false',
                              description='true = run the HOME -> A -> B -> charger mission automatically'),
        sim, localization, navigation, walker, mission_node,
    ])
