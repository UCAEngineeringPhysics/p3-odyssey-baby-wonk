import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
import math


class WonkletNavigator(Node):
    def __init__(self):
        super().__init__("wonklet_navigator")
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            "navigate_to_pose"
        )
        self.get_logger().info("Wonklet Navigator initialized!")

    def send_goal(self, x, y, yaw=0.0):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = math.sin(yaw / 2)
        goal_msg.pose.pose.orientation.w = math.cos(yaw / 2)
        self.get_logger().info(f"Sending goal: x={x}, y={y}")
        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected!")
            return
        self.get_logger().info("Goal accepted!")
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result()
        status = result.status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal succeeded! Coffee delivered!")
        else:
            self.get_logger().warn(f"Goal failed with status: {status}")
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"Distance remaining: {feedback.distance_remaining:.2f}m"
        )


def main(args=None):
    rclpy.init(args=args)
    navigator = WonkletNavigator()
    TARGET_X = 10.5
    TARGET_Y = 0.0
    TARGET_YAW = 0.0
    navigator.send_goal(TARGET_X, TARGET_Y, TARGET_YAW)
    rclpy.spin(navigator)


if __name__ == "__main__":
    main()
