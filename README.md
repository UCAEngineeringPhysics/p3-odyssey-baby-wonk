# BabyWonk: The Odyssey

Autonomous navigation of the BabyWonk differential drive robot from Room 159 (Dr. Chen's lab) to Room 171 (PAE Department office) in the Lewis Science Center, delivering a cup of coffee.

**Maintainer:** mgarrett1515 — mgarrett12@cub.uca.edu

**Packages:**
- [babywonk_bringup](babywonk_bringup/) — robot hardware bringup (motors, odometry, IMU, lidar)
- [babywonk_navigation](babywonk_navigation/) — SLAM mapping, AMCL localization, Nav2, navigator node

---

## Coffee Delivery Solution
## Bottom Support
<img width="420" height="458" alt="Screenshot from 2026-05-01 09-46-13" src="https://github.com/user-attachments/assets/56d8e6b9-4553-4768-b505-b43748920c00" />

## Top Support
<img width="529" height="523" alt="Screenshot from 2026-05-01 09-51-12" src="https://github.com/user-attachments/assets/1af56505-1528-4b84-ab86-5460ccae20e9" />



# Installation Guide
## Steps for Installation
1. 3d Print both Pieces accordingly
   
2. Once done, the underlaying connection pieces, match up with the "BASE" and "ROOF" respectively
   
3. I did not drill holes to allow for user customability, given this the user will need to decide the level of "secure" they want their cupholder to be.
   
4. Based on this level, at any point along the top or bottom mount holes should be drilled with 3mm screws placed through said holes and secured with a nut.

# Example Pictures

<img width="701" height="399" alt="Screenshot from 2026-05-01 10-28-37" src="https://github.com/user-attachments/assets/7bed753a-23bc-4459-b88d-1d24e7ef81a6" />
<img width="455" height="409" alt="Screenshot from 2026-05-01 10-29-16" src="https://github.com/user-attachments/assets/b8de5129-66b6-422d-9193-b87c23343b54" />

 


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

