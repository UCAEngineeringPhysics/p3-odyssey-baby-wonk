import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from mcap_ros2.reader import read_ros2_messages


def get_latest_bag():
    bag_folders = glob.glob('bags/rosbag2_*')
    if not bag_folders:
        return None
    return max(bag_folders, key=os.path.getctime)


def cleanup_old_plots():
    files_to_remove = ['trajectory_final.png', 'imu_analysis.png']
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted old version of {f}")


def main():
    cleanup_old_plots()

    latest_bag = get_latest_bag()
    if not latest_bag:
        print("Error: No bag files found in the bags/ directory.")
        return

    mcap_files = glob.glob(os.path.join(latest_bag, "*.mcap"))
    if not mcap_files:
        print("Error: No MCAP file found in the latest bag folder.")
        return

    mcap_file = mcap_files[0]
    print(f"Processing Latest Run: {mcap_file}")

    odom_data = []
    imu_data = []

    for msg_view in read_ros2_messages(mcap_file):
        topic = msg_view.channel.topic
        msg = msg_view.ros_msg

        if topic == "/odom":
            odom_data.append({
                'x': msg.pose.pose.position.x,
                'y': msg.pose.pose.position.y,
                'time': msg_view.publish_time_ns / 1e9,
            })
        elif topic == "/imu":
            imu_data.append({
                'accel_z': msg.linear_acceleration.z,
                'time': msg_view.publish_time_ns / 1e9,
            })

    if odom_data:
        df_odom = pd.DataFrame(odom_data)
        plt.figure(figsize=(10, 7))
        plt.plot(df_odom['x'], df_odom['y'], label='BabyWonk Path', color='#1f77b4', lw=2)
        plt.axvline(x=2.0, color='red', linestyle='--', label='2.0m Goal Line')
        plt.scatter(df_odom['x'].iloc[0], df_odom['y'].iloc[0], color='green', s=100, label='Start')
        plt.title('BabyWonk Autonomous Navigation: X-Y Trajectory', fontsize=14)
        plt.xlabel('X Position (meters)', fontsize=12)
        plt.ylabel('Y Lateral Drift (meters)', fontsize=12)
        plt.axis('equal')
        plt.grid(True, which='both', linestyle='--', alpha=0.5)
        plt.legend()
        plt.savefig('trajectory_final.png', dpi=300)
        print("Created: trajectory_final.png")

    if imu_data:
        df_imu = pd.DataFrame(imu_data)
        plt.figure(figsize=(12, 5))
        plt.plot(df_imu['time'] - df_imu['time'].min(), df_imu['accel_z'], color='#ff7f0e', alpha=0.8)
        plt.axhline(y=9.81, color='black', lw=1, ls=':', label='Gravity (9.81 m/s²)')
        plt.title('Sensor Analysis: IMU Vertical Acceleration', fontsize=14)
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('Acceleration Z (m/s²)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig('imu_analysis.png', dpi=300)
        print("Created: imu_analysis.png")


if __name__ == "__main__":
    main()
