"""Keyboard-only teleop — no hardware required.
Run alongside bringup_launch.py to drive with the keyboard.
  ros2 run teleop_twist_keyboard teleop_twist_keyboard
This launch file is a convenience wrapper that just reminds you.
Actually launching teleop_twist_keyboard requires an interactive terminal,
so run it directly in a separate terminal instead.
"""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # joy_node + teleop_twist_joy for gamepad-only mode (no lidar/ekf)
    # Useful for quick motor/encoder testing without the full stack.
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
        ),
        Node(
            package='teleop_twist_joy',
            executable='teleop_twist_joy_node',
            name='teleop_twist_joy_node',
            output='screen',
            parameters=[{'enable_button': 4,
                         'enable_turbo_button': 5,
                         'axis_linear.x': 1,
                         'scale_linear.x': 0.4,
                         'axis_angular.yaw': 0,
                         'scale_angular.yaw': 1.2}],
        ),
    ])
