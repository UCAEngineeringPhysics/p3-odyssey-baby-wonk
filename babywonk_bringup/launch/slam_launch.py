"""SLAM mapping launch.
Drive around with the gamepad while slam_toolbox builds the map.
Save the map when done:
  ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
"""
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_bringup')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false', choices=['true', 'false'],
    )

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(pkg / 'launch' / 'bringup_launch.py')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'enable_teleop': 'true',   # drive around to build the map
        }.items(),
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            str(pkg / 'config' / 'slam_params.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        bringup_launch,
        slam_node,
    ])
