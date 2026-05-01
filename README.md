# BabyWonk: The Odyssey

Autonomous navigation of the BabyWonk differential drive robot from Room 159 (Dr. Chen's lab) to Room 171 (PAE Department office) in the Lewis Science Center, delivering a cup of coffee.

**Maintainer:** mgarrett1515 — mgarrett12@cub.uca.edu

**Packages:**
- [babywonk_bringup](babywonk_bringup/) — robot hardware bringup (motors, odometry, IMU, lidar)
- [babywonk_navigation](babywonk_navigation/) — SLAM mapping, AMCL localization, Nav2, navigator node

---

## Coffee Delivery Solution

<!-- TODO: Add sketch/photo of your cup holder design here -->
<!-- TODO: Add critical dimensions -->

### Installation Guide

<!-- TODO: Describe how to mount the cup holder onto the robot -->
<!-- TODO: Include steps with photos if possible -->

---

## Software Setup

### Raspberry Pi Dependencies

On a freshly installed ROS 2 Jazzy system, install the following:

```bash
sudo apt update
sudo apt install -y \
    ros-jazzy-robot-localization \
    ros-jazzy-rplidar-ros \
    ros-jazzy-teleop-twist-joy \
    ros-jazzy-joy \
    ros-jazzy-tf-transformations \
    python3-serial \
    python3-transforms3d
```

### Server Computer Dependencies

```bash
sudo apt update
sudo apt install -y \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    ros-jazzy-tf-transformations \
    python3-transforms3d
```

### Building the Workspace

```bash
mkdir -p ~/project_3_ws/src
cd ~/project_3_ws/src
git clone <repository_url>
cd ~/project_3_ws
colcon build --symlink-install
source ~/project_3_ws/install/setup.bash
```

---

## Usage

### Creating a Map

Place the robot at the desired starting location. Open two terminals:

**Terminal 1 — Robot bringup:**
```bash
source ~/project_3_ws/install/setup.bash
ros2 launch babywonk_bringup bringup_launch.py
```

**Terminal 2 — SLAM mapping:**
```bash
source ~/project_3_ws/install/setup.bash
ros2 launch babywonk_navigation pi_mapping_launch.py
```

Drive the robot through the full route using the PS4 controller (hold L1 to enable, left stick to move). Once mapping is complete, save the map before shutting down.

### Saving the Map

```bash
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map --ros-args -p save_map_timeout:=10.0
```

This saves `my_map.pgm` and `my_map.yaml` to `~/maps/`. Update the map path in:
- `src/babywonk_navigation/launch/navigation_launch.py`
- `src/babywonk_navigation/configs/localization_params.yaml`

### Running Autonomous Navigation

Place the robot at the exact position and orientation used when the map was created. Open two terminals:

**Terminal 1 — Navigator (run first, waits for Nav2):**
```bash
source ~/project_3_ws/install/setup.bash
ros2 run babywonk_navigation navigator
```

**Terminal 2 — Nav2 launch (use sleep to allow time to position the robot):**
```bash
sleep 20 && source ~/project_3_ws/install/setup.bash && ros2 launch babywonk_navigation navigation_launch.py
```

The robot will autonomously navigate through the corridor route via waypoints and print `ODYSSEY COMPLETE` upon arrival at Room 171.

---

## Map Files

The map used for navigation is located in `~/maps/` on the robot's Raspberry Pi:
- `odyssey_map_run6.pgm` — occupancy grid image

<img width="497" height="615" alt="odyssey_map_run6" src="https://github.com/user-attachments/assets/918a8335-2f59-4312-b6d6-4a3be6ff7949" />

- `odyssey_map_run6.yaml` — map metadata (resolution, origin)
---

## Package Overview

| Package | Runs On | Purpose |
|---|---|---|
| `babywonk_bringup` | Raspberry Pi | Motor control, odometry, IMU, lidar, TF |
| `babywonk_navigation` | Raspberry Pi | SLAM mapping, AMCL localization, Nav2, navigator node |

### Node Summary

| Node | Subscribes | Publishes |
|---|---|---|
| `pico_interface` | `/cmd_vel` | `/odom`, `/imu` |
| `ekf_node` | `/odom`, `/imu` | `/odometry/filtered`, `odom→base_link` TF |
| `rplidar` | — | `/scan` |
| `amcl` | `/scan`, `/map` | `map→odom` TF |
| `planner_server` | `/map`, `/scan` | `/plan` |
| `controller_server` | `/plan`, `/scan` | `/cmd_vel` |
| `navigator` | action feedback | `NavigateToPose` action goals |<img width="497" height="615" alt="odyssey_map_run6" src="https://github.com/user-attachments/assets/6ae35449-80f3-4fba-9de8-51b8079b94d6" />

