import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 as cv


class ArucoDetector(Node):
    """Detects ArUco markers from /camera/image_raw and publishes annotated image.
    Requires camera_ros camera_node to be running first.
    """

    def __init__(self):
        super().__init__('aruco_detector')
        reliable_qos = rclpy.qos.QoSProfile(
            depth=10,
            reliability=rclpy.qos.QoSReliabilityPolicy.RELIABLE,
        )
        self.camera_sub = self.create_subscription(
            Image, '/camera/image_raw', self.detect_aruco, reliable_qos,
        )
        self.detection_pub = self.create_publisher(
            Image, '/camera/aruco_detection', reliable_qos,
        )
        aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
        aruco_params = cv.aruco.DetectorParameters()
        self.detector = cv.aruco.ArucoDetector(aruco_dict, aruco_params)
        self.bridge = CvBridge()

    def detect_aruco(self, msg):
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        corners, ids, _ = self.detector.detectMarkers(cv_img)
        if ids is not None:
            self.get_logger().info(f'Detected markers: {ids.flatten().tolist()}')
            for i in range(len(ids)):
                top_left = corners[i][0][0].astype(int)
                bot_right = corners[i][0][2].astype(int)
                cv_img = cv.rectangle(cv_img, top_left, bot_right, (131, 44, 88), 5)
                cv.putText(
                    cv_img,
                    str(ids[i][0]),
                    (top_left[0], top_left[1] - 10),
                    cv.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (131, 44, 88),
                    2,
                    cv.LINE_AA,
                )
        self.detection_pub.publish(self.bridge.cv2_to_imgmsg(cv_img, encoding='bgr8'))


def main(args=None):
    rclpy.init(args=args)
    node = ArucoDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
