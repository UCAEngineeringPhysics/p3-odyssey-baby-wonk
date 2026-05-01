"""Autonomous navigation launch — LiDAR + odometry reactive driving.
Equivalent to project 2's encodom_homer_launch.py.
  ros2 launch babywonk_bringup navigator_launch.py
"""
from math import pi
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_bringup')

    pico_node = Node(
        package='babywonk_bringup',
        executable='pico_interface',
        output='screen',
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[str(pkg / 'config' / 'ekf.yaml')],
    )

    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg / 'launch' / 'rplidar_launch.py')),
    )

    footprint_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '-0.0325',
                   '--yaw', '0', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link',
                   '--child-frame-id', 'base_footprint'],
    )
    imu_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0.07',
                   '--yaw', '0', '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link',
                   '--child-frame-id', 'imu_link'],
    )
    lidar_tf = Node(
        package='tf2_ros', executable='static_transform_publisher',
        arguments=['--x', '-0.021', '--y', '0', '--z', '0.12',
                   '--yaw', str(pi), '--pitch', '0', '--roll', '0',
                   '--frame-id', 'base_link',
                   '--child-frame-id', 'lidar_link'],
    )

    navigator_node = Node(
        package='babywonk_bringup',
        executable='navigator',
        output='screen',
    )

    return LaunchDescription([
        pico_node,
        ekf_node,
        rplidar_launch,
        footprint_tf,
        imu_tf,
        lidar_tf,
        navigator_node,
    ])
