import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarTest(Node):
    """Diagnostic tool — prints LiDAR distance at 0°, 90°, 180°, 270°."""

    def __init__(self):
        super().__init__('lidar_test_node')
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.get_logger().info('LiDAR diagnostic tool active.')

    def scan_callback(self, msg):
        def clean(val):
            return 9.99 if (str(val) in ('inf', 'nan')) else val

        front = clean(msg.ranges[0])
        left = clean(msg.ranges[90])
        back = clean(msg.ranges[180])
        right = clean(msg.ranges[270])
        self.get_logger().info(
            f'0°: {front:.2f}m  |  90°: {left:.2f}m  |  180°: {back:.2f}m  |  270°: {right:.2f}m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = LidarTest()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
