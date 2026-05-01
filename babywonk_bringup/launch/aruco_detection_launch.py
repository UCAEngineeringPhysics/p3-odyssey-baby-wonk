from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_path('babywonk_bringup')
    default_rviz = str(pkg / 'rviz' / 'camera.rviz')

    rviz_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=default_rviz,
        description='Path to RViz config file',
    )

    camera_node = Node(package='camera_ros', executable='camera_node')

    aruco_node = Node(
        package='babywonk_bringup',
        executable='aruco_detector',
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )

    return LaunchDescription([
        rviz_arg,
        camera_node,
        aruco_node,
        rviz_node,
    ])
