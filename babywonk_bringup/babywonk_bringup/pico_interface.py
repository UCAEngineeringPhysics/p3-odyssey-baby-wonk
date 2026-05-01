from math import sin, cos, atan2
import serial
import rclpy
from rclpy.node import Node
from tf_transformations import quaternion_about_axis
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry


class PicoInterface(Node):
    def __init__(self):
        super().__init__(node_name='pico_interface')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        port = self.get_parameter('serial_port').get_parameter_value().string_value

        self.pico = serial.Serial(port, 115200, timeout=0.01)
        self.pico.reset_input_buffer()
        self.create_timer(0.02, self._tick)  # 50 Hz

        self.cmd_vel_sub = self.create_subscription(
            Twist, 'cmd_vel', self._on_cmd_vel, qos_profile=1
        )
        self.odom_pub = self.create_publisher(Odometry, '/odom', qos_profile=1)
        self.imu_pub = self.create_publisher(Imu, '/imu', qos_profile=1)

        keys = ['enc_lin_vel', 'enc_ang_vel',
                'acc_x', 'acc_y', 'acc_z',
                'omg_x', 'omg_y', 'omg_z']
        self.data = {k: 0.0 for k in keys}
        self.targ_lin = 0.0
        self.targ_ang = 0.0
        self.pose = {'x': 0.0, 'y': 0.0, 'theta': 0.0}
        self.prev_ts = self.get_clock().now()
        self.cmd_vel_ts = self.get_clock().now()

        self.get_logger().info(f'PicoInterface connected on {port}')

    def _on_cmd_vel(self, msg: Twist):
        self.cmd_vel_ts = self.get_clock().now()
        self.targ_lin = msg.linear.x
        self.targ_ang = msg.angular.z

    def _tick(self):
        # Safety stop: zero velocity if no cmd_vel for 0.5 s
        if (self.get_clock().now() - self.cmd_vel_ts).nanoseconds > 500_000_000:
            self.targ_lin = 0.0
            self.targ_ang = 0.0

        # TX to Pico — flush stale outgoing commands before writing
        self.pico.reset_output_buffer()
        self.pico.write(f'{self.targ_lin:.3f},{self.targ_ang:.3f}\n'.encode())

        # RX from Pico — drain entire buffer, keep only the latest line
        raw = None
        while self.pico.inWaiting() > 0:
            line = self.pico.readline().decode('utf-8', 'ignore').strip()
            if line:
                raw = line
        if raw:
            parts = raw.split(',')
            if len(parts) == 8:
                try:
                    self.data.update(zip(self.data.keys(), map(float, parts)))
                except ValueError:
                    pass

        now = self.get_clock().now()
        dt = (now - self.prev_ts).nanoseconds * 1e-9
        self.prev_ts = now

        # Dead-reckoning pose integration
        th = self.pose['theta']
        self.pose['x'] += self.data['enc_lin_vel'] * cos(th) * dt
        self.pose['y'] += self.data['enc_lin_vel'] * sin(th) * dt
        self.pose['theta'] = atan2(
            sin(th + self.data['enc_ang_vel'] * dt),
            cos(th + self.data['enc_ang_vel'] * dt),
        )

        quat = quaternion_about_axis(self.pose['theta'], (0, 0, 1))
        stamp = now.to_msg()

        # Odometry
        odom = Odometry()
        odom.header.stamp = stamp
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.pose['x']
        odom.pose.pose.position.y = self.pose['y']
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.x = quat[0]
        odom.pose.pose.orientation.y = quat[1]
        odom.pose.pose.orientation.z = quat[2]
        odom.pose.pose.orientation.w = quat[3]
        odom.twist.twist.linear.x = self.data['enc_lin_vel']
        odom.twist.twist.angular.z = self.data['enc_ang_vel']
        self.odom_pub.publish(odom)

        # IMU
        imu = Imu()
        imu.header.stamp = stamp
        imu.header.frame_id = 'imu_link'
        imu.linear_acceleration.x = self.data['acc_x']
        imu.linear_acceleration.y = self.data['acc_y']
        imu.linear_acceleration.z = self.data['acc_z']
        imu.angular_velocity.x = self.data['omg_x']
        imu.angular_velocity.y = self.data['omg_y']
        imu.angular_velocity.z = self.data['omg_z']
        self.imu_pub.publish(imu)


def main(args=None):
    rclpy.init(args=args)
    node = PicoInterface()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
