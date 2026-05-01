"""SLAM mapping launch — run on the SERVER while driving the robot manually.
After mapping, save the map:
  ros2 run nav2_map_server map_saver_cli -f ~/maps/odyssey_map

Pi terminals (run first):
  ros2 run babywonk_bringup pico_interface
  ros2 launch babywonk_bringup rplidar_launch.py
"""
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_navigation')
    slam_pkg = get_package_share_path('slam_toolbox')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false', choices=['true', 'false'],
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(slam_pkg / 'launch' / 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': str(pkg / 'configs' / 'mapping_params.yaml'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', str(pkg / 'rviz' / 'mapping.rviz')],
    )

    return LaunchDescription([
        use_sim_time_arg,
        slam_launch,
        rviz_node,
    ])
