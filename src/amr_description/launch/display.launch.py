import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc = get_package_share_directory('amr_description')
    xacro_file = os.path.join(desc, 'urdf', 'amr.urdf.xacro')
    rviz_config = os.path.join(desc, 'rviz', 'display.rviz')   # NEW line

    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description}])

    jsp_gui = Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui')

    rviz = Node(package='rviz2', executable='rviz2',
                arguments=['-d', rviz_config])                  # CHANGED line

    return LaunchDescription([rsp, jsp_gui, rviz])
