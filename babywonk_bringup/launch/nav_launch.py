"""Autonomous navigation launch (requires a saved map).
Usage:
  ros2 launch babywonk_bringup nav_launch.py map:=/home/mg/maps/my_map.yaml

Then use RViz2 Nav2 plugin or:
  ros2 topic pub /goal_pose geometry_msgs/PoseStamped ...
"""
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_bringup')
    nav2_pkg = get_package_share_path('nav2_bringup')

    map_arg = DeclareLaunchArgument(
        'map', description='Full path to the .yaml map file',
    )
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false', choices=['true', 'false'],
    )

    # Hardware bringup — teleop disabled so Nav2 owns cmd_vel
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg / 'launch' / 'bringup_launch.py')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'enable_teleop': 'false',
        }.items(),
    )

    # Localization: map_server + AMCL
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(nav2_pkg / 'launch' / 'localization_launch.py')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'map': LaunchConfiguration('map'),
            'params_file': str(pkg / 'config' / 'nav2_params.yaml'),
        }.items(),
    )

    # Navigation stack: planners + controllers + behaviors + bt_navigator
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(nav2_pkg / 'launch' / 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'params_file': str(pkg / 'config' / 'nav2_params.yaml'),
        }.items(),
    )

    return LaunchDescription([
        map_arg,
        use_sim_time_arg,
        bringup_launch,
        localization_launch,
        nav2_launch,
    ])
