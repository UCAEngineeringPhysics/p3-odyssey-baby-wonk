"""Autonomous navigation launch — starts only the Nav2 nodes we need.
Run on the Pi after mapping is complete.

Terminal 2 (run first — waits for Nav2):
  source ~/project_3_ws/install/setup.bash
  ros2 run babywonk_navigation navigator

Terminal 1:
  sleep 20 && source ~/project_3_ws/install/setup.bash
  ros2 launch babywonk_navigation navigation_launch.py
"""
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_navigation')
    bringup_pkg = get_package_share_path('babywonk_bringup')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=str(pkg / 'maps' / 'odyssey_map_run6'),
        description='Full path to saved map file (no extension)',
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false', choices=['true', 'false'],
    )

    # ── Robot bringup (pico, EKF, lidar, TFs — no teleop) ───────────────────
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(bringup_pkg / 'launch' / 'bringup_launch.py')
        ),
        launch_arguments={'enable_teleop': 'false'}.items(),
    )

    # ── map_server — serves the saved pgm/yaml map ───────────────────────────
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': str(pkg / 'maps' / 'odyssey_map_run6.yaml'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    params = str(pkg / 'configs' / 'nav2_params.yaml')

    # ── AMCL — particle filter localization, publishes map→odom TF ──────────
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params],
    )

    # ── Nav2 nodes (only what we need — no collision_monitor/docking/route) ─
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        output='screen',
        parameters=[params],
    )
    smoother_server = Node(
        package='nav2_smoother',
        executable='smoother_server',
        output='screen',
        parameters=[params],
    )
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        output='screen',
        parameters=[params],
    )
    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        output='screen',
        parameters=[params],
    )
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        output='screen',
        parameters=[params],
    )
    waypoint_follower = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        output='screen',
        parameters=[params],
    )
    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        output='screen',
        parameters=[params],
    )
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[params],
    )

    return LaunchDescription([
        map_arg,
        use_sim_time_arg,
        bringup_launch,
        map_server,
        amcl,
        controller_server,
        smoother_server,
        planner_server,
        behavior_server,
        bt_navigator,
        waypoint_follower,
        velocity_smoother,
        lifecycle_manager,
    ])
