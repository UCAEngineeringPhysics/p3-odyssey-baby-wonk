"""Headless mapping launch — runs on the Pi with no monitor.
slam_toolbox builds the map and publishes /map over the network.
View it from any PC on the same ROS_DOMAIN_ID with:
  ros2 launch babywonk_navigation create_map_launch.py
Or just rviz2 if the PC only has ROS 2 base installed.
"""
from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    bringup_pkg = get_package_share_path('babywonk_bringup')
    nav_pkg = get_package_share_path('babywonk_navigation')

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(bringup_pkg / 'launch' / 'bringup_launch.py')
        ),
        launch_arguments={'enable_teleop': 'true'}.items(),
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            str(nav_pkg / 'configs' / 'mapping_params.yaml'),
            {'autostart': True},
        ],
    )

    # Retry configure until slam_toolbox is ready, then activate
    configure_slam = TimerAction(
        period=5.0,
        actions=[ExecuteProcess(
            cmd=['bash', '-c',
                 'until ros2 lifecycle set /slam_toolbox configure; do sleep 1; done'],
            output='screen',
        )],
    )

    activate_slam = TimerAction(
        period=7.0,
        actions=[ExecuteProcess(
            cmd=['bash', '-c',
                 'until ros2 lifecycle set /slam_toolbox activate; do sleep 1; done'],
            output='screen',
        )],
    )

    return LaunchDescription([
        bringup_launch,
        slam_node,
        configure_slam,
        activate_slam,
    ])
