from math import pi
from pathlib import Path
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_bringup')

    # ── Launch arguments ────────────────────────────────────────────────────
    serial_port_arg = DeclareLaunchArgument(
        'serial_port', default_value='/dev/ttyACM0',
        description='Serial port for Pico USB connection',
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false', choices=['true', 'false'],
    )
    enable_teleop_arg = DeclareLaunchArgument(
        'enable_teleop', default_value='true', choices=['true', 'false'],
        description='Launch gamepad teleop (disable when running Nav2)',
    )

    # ── Pico serial bridge ───────────────────────────────────────────────────
    pico_node = Node(
        package='babywonk_bringup',
        executable='pico_interface',
        output='screen',
        parameters=[{'serial_port': LaunchConfiguration('serial_port')}],
    )

    # ── EKF (fuses /odom + /imu → /odometry/filtered + odom→base_link TF) ──
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            str(pkg / 'config' / 'ekf.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    # ── RPLidar ─────────────────────────────────────────────────────────────
    rplidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg / 'launch' / 'rplidar_launch.py')),
    )

    # ── Static TFs ──────────────────────────────────────────────────────────
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

    # ── Gamepad teleop (conditional) ────────────────────────────────────────
    teleop_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(get_package_share_path('teleop_twist_joy') / 'launch' / 'teleop-launch.py')
        ),
        launch_arguments={'config_filepath': str(pkg / 'config' / 'gamepad.yaml')}.items(),
        condition=IfCondition(LaunchConfiguration('enable_teleop')),
    )

    return LaunchDescription([
        serial_port_arg,
        use_sim_time_arg,
        enable_teleop_arg,
        pico_node,
        ekf_node,
        rplidar_launch,
        footprint_tf,
        imu_tf,
        lidar_tf,
        teleop_launch,
    ])
