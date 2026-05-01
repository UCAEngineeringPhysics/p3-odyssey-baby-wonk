"""
Odyssey Navigator — drives BabyWonk from Room 159 → 171 via waypoints.
Waypoints force Nav2 through the correct corridor instead of shortcutting
through unmapped/unknown space.
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler


# ── Waypoints: (x_m, y_m, yaw_rad) in map frame ─────────────────────────────
# WP 0: intermediate checkpoint along the correct corridor path
# WP 1: final goal — Room 171
# Update WP 0 coordinates after checking RViz for a mid-route point.
WAYPOINTS = [
    ( 2.00087, -0.00898, 0.0),  # 1 — clear of start
    ( 2.00087, -6.54146, 0.0),  # 2 — bottom corridor (directly south of WP1)
    (15.51080, -6.32277, 0.0),  # 3 — bottom right corner
    (14.26590, 12.94820, 0.0),  # 4 — right corridor heading up
    (11.50000, 12.90000, 0.0),  # 5 — Room 171 goal
]
# ─────────────────────────────────────────────────────────────────────────────


class OdysseyNavigator(Node):
    def __init__(self):
        super().__init__('odyssey_navigator')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._wp_index = 0
        self._goal_sent = False
        self.create_timer(1.0, self._try_send_goal)
        self.get_logger().info('Odyssey Navigator ready — waiting for Nav2...')

    def _try_send_goal(self):
        if self._goal_sent:
            return
        if not self._client.wait_for_server(timeout_sec=0.0):
            self.get_logger().info(
                'Waiting for Nav2 navigate_to_pose action server...',
                throttle_duration_sec=5.0,
            )
            return
        self._send_waypoint(self._wp_index)

    def _send_waypoint(self, index):
        self._goal_sent = True
        x, y, yaw = WAYPOINTS[index]

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        q = quaternion_from_euler(0.0, 0.0, yaw)
        goal.pose.pose.orientation.x = q[0]
        goal.pose.pose.orientation.y = q[1]
        goal.pose.pose.orientation.z = q[2]
        goal.pose.pose.orientation.w = q[3]

        label = 'FINAL GOAL' if index == len(WAYPOINTS) - 1 else f'waypoint {index + 1}/{len(WAYPOINTS)}'
        self.get_logger().info(
            f'Sending {label} → x={x:.2f} m, y={y:.2f} m, yaw={yaw:.2f} rad'
        )
        future = self._client.send_goal_async(goal, feedback_callback=self._on_feedback)
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warn('Goal rejected — retrying...')
            self._goal_sent = False
            return
        self.get_logger().info('Goal ACCEPTED')
        handle.get_result_async().add_done_callback(self._on_result)

    def _on_feedback(self, feedback):
        dist = feedback.feedback.distance_remaining
        self.get_logger().info(
            f'Distance remaining: {dist:.2f} m',
            throttle_duration_sec=3.0,
        )

    def _on_result(self, future):
        status = future.result().status
        if status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().error(
                f'Waypoint {self._wp_index + 1} FAILED (status {status}) — aborting mission.'
            )
            rclpy.shutdown()
            return

        self._wp_index += 1
        if self._wp_index >= len(WAYPOINTS):
            self.get_logger().info('')
            self.get_logger().info('=' * 52)
            self.get_logger().info('  ODYSSEY COMPLETE — Coffee delivered to Room 171!')
            self.get_logger().info('=' * 52)
            self.get_logger().info('')
            rclpy.shutdown()
            return

        self.get_logger().info(
            f'Waypoint {self._wp_index} reached — continuing to next...'
        )
        self._goal_sent = False


def main(args=None):
    rclpy.init(args=args)
    node = OdysseyNavigator()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
