import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class Navigator(Node):
    def __init__(self):
        super().__init__('navigator')
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Mission settings
        self.prep_time = 15.0
        self.target_dist = 10.25
        self.straight_dist = 0.7
        self.bias_duration = 1.75

        # Tuning
        self.stop_dist = 0.40
        self.clear_dist = 0.85
        self.move_speed = 0.10
        self.home_stop_dist = 0.72

        self.start_time = time.time()
        self.bias_start_time = None
        self.total_dist = 0.0
        self.last_pos = None
        self.active = False
        self.is_spinning = False
        self.homing_mode = False

        self.get_logger().info('Navigator ready — waiting for prep time...')

    def odom_callback(self, msg):
        if not self.active:
            return
        p = msg.pose.pose.position
        if self.last_pos:
            self.total_dist += math.sqrt(
                (p.x - self.last_pos.x) ** 2 + (p.y - self.last_pos.y) ** 2
            )
        self.last_pos = p

    def detect_bucket(self, msg):
        num_pts = len(msg.ranges)
        clusters = []
        current_cluster = []

        start_idx = int(num_pts * 0.75)
        end_idx = int(num_pts * (15.0 / 360.0))
        indices = list(range(start_idx, num_pts)) + list(range(0, end_idx))

        for i in indices:
            d = msg.ranges[i]
            if d < 0.12 or d > 4.0:
                if current_cluster:
                    clusters.append(current_cluster)
                    current_cluster = []
                continue
            if not current_cluster:
                current_cluster.append(i)
            else:
                prev_idx = current_cluster[-1]
                angle_i = (i / num_pts) * 2 * math.pi
                angle_prev = (prev_idx / num_pts) * 2 * math.pi
                dx = d * math.cos(angle_i) - msg.ranges[prev_idx] * math.cos(angle_prev)
                dy = d * math.sin(angle_i) - msg.ranges[prev_idx] * math.sin(angle_prev)
                if math.hypot(dx, dy) < 0.25:
                    current_cluster.append(i)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [i]

        if current_cluster:
            clusters.append(current_cluster)

        valid_targets = []
        for c in clusters:
            if len(c) < 3:
                continue
            first_idx, last_idx = c[0], c[-1]
            d_first = msg.ranges[first_idx]
            d_last = msg.ranges[last_idx]
            a_first = (first_idx / num_pts) * 2 * math.pi
            a_last = (last_idx / num_pts) * 2 * math.pi
            width = math.hypot(
                d_first * math.cos(a_first) - d_last * math.cos(a_last),
                d_first * math.sin(a_first) - d_last * math.sin(a_last),
            )
            if 0.15 < width < 0.6:
                avg_d = sum(msg.ranges[i] for i in c) / len(c)
                avg_idx_sum = sum(
                    (idx + num_pts) if idx < end_idx else idx for idx in c
                )
                avg_idx = avg_idx_sum / len(c)
                if avg_idx >= num_pts:
                    avg_idx -= num_pts
                angle_deg = (avg_idx / num_pts) * 360.0
                steering_angle = angle_deg - 360.0 if angle_deg > 180 else angle_deg
                valid_targets.append((avg_d, steering_angle))

        if valid_targets:
            valid_targets.sort(key=lambda x: x[0])
            return valid_targets[0]

        return None, None

    def lidar_callback(self, msg):
        now = time.time()
        if (now - self.start_time) < self.prep_time:
            return
        self.active = True

        # Homing phase
        if self.total_dist >= self.target_dist or self.homing_mode:
            self.homing_mode = True
            bucket_dist, steering_angle = self.detect_bucket(msg)
            twist = Twist()

            if bucket_dist is not None:
                if bucket_dist <= self.home_stop_dist:
                    self.get_logger().info('Target reached — stopping.')
                    self.cmd_pub.publish(Twist())
                    time.sleep(0.5)
                    raise SystemExit

                twist.angular.z = max(-0.4, min(0.4, steering_angle * 0.02))
                if abs(steering_angle) > 15:
                    twist.linear.x = 0.0
                    self.get_logger().info(
                        f'Pivoting {steering_angle:.1f} deg',
                        throttle_duration_sec=1.0,
                    )
                else:
                    twist.linear.x = 0.05
                    self.get_logger().info(
                        f'Homing: {bucket_dist:.2f} m away',
                        throttle_duration_sec=1.0,
                    )
            else:
                self.get_logger().info('Searching...', throttle_duration_sec=1.5)
                twist.angular.z = -0.3

            self.cmd_pub.publish(twist)
            return

        # Standard obstacle-avoidance navigation
        num_pts = len(msg.ranges)

        def get_slice_dist(center_deg, width_deg):
            center_idx = int(num_pts * (center_deg / 360.0))
            half_width = int(num_pts * (width_deg / 720.0))
            start = (center_idx - half_width) % num_pts
            end = (center_idx + half_width) % num_pts
            pts = (
                msg.ranges[start:end]
                if start < end
                else list(msg.ranges[start:]) + list(msg.ranges[:end])
            )
            valid = [r for r in pts if 0.12 < r < 8.0]
            return min(valid) if valid else 8.0

        d_front = get_slice_dist(0, 30)
        d_left = get_slice_dist(35, 40) * 0.8 + get_slice_dist(70, 30) * 0.2
        d_right = get_slice_dist(325, 40) * 0.8 + get_slice_dist(290, 30) * 0.2

        twist = Twist()

        if self.is_spinning:
            if d_front > self.clear_dist:
                self.is_spinning = False
            else:
                twist.angular.z = (
                    0.35 if self.total_dist < 3.0 else (0.35 if d_left > d_right else -0.35)
                )
        else:
            if d_front < self.stop_dist:
                self.is_spinning = True
            else:
                twist.linear.x = self.move_speed
                if self.total_dist < self.straight_dist:
                    twist.angular.z = 0.0
                else:
                    if self.bias_start_time is None:
                        self.bias_start_time = time.time()
                    if (time.time() - self.bias_start_time) < self.bias_duration:
                        twist.angular.z = ((d_left * 1.5) - d_right) * 0.45
                    else:
                        twist.angular.z = (d_left - d_right) * 0.5

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = Navigator()
    try:
        rclpy.spin(node)
    except SystemExit:
        node.get_logger().info('Navigator terminated.')
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        rclpy.shutdown()


if __name__ == '__main__':
    main()
