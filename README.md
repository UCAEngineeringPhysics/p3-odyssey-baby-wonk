[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/7KaPTW5f)
# The Odyssey
**Maintainer:** Lillian Slaton | lslaton@cub.uca.edu

Autonomous navigation project for the HomeR robot. The robot navigates from Room 159 to Room 171 in the Lewis Science Center, delivering a cup of coffee to the front desk.

---

## Coffee Transportation Solution

### Mechanical Design
The coffee cup holder is a 3D-printed cylindrical cradle mounted on the top platform of the robot. It is designed to hold a standard 12 oz cup (diameter: 82mm at base, 95mm at top, height: 145mm).

Key design decisions:
- Low center of gravity mount to reduce spilling during turns
- Friction-fit ring to secure cup without mechanical fasteners
- Mounted centered over the robot's wheelbase for balanced weight distribution

### Hardware Installation Guide
1. Print the cup holder using PLA filament (STL files in `/images/`)
2. Place the cup holder on the top platform of the robot
3. Secure with M3 bolts through the four mounting holes
4. Insert the 12 oz cup into the holder — it should fit snugly with no lateral movement
5. Verify the cup does not exceed the height of the LiDAR mounting posts

---

## Software Usage Instructions

### Installing Dependencies on Raspberry Pi
```bash
# Install ROS 2 Jazzy
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-jazzy-ros-base -y
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

# Install homer_bringup
sudo apt install python3-rosdep python3-colcon-common-extensions git -y
sudo rosdep init && rosdep update
mkdir -p ~/homer_ws/src && cd ~/homer_ws/src
git clone https://github.com/linzhanguca/homer_bringup.git
cd ~/homer_ws
rosdep install -y --from-paths src --ignore-src --rosdistro $ROS_DISTRO
colcon build
echo "source ~/homer_ws/install/local_setup.bash" >> ~/.bashrc
source ~/.bashrc

# Install wonklet package
cd ~/homer_ws/src
git clone https://github.com/UCAEngineeringPhysics/p3-odyssey-baby-wonk.git
cp -r p3-odyssey-baby-wonk/wonklet .
cd ~/homer_ws
colcon build
source ~/.bashrc
```

### Installing Dependencies on Server Computer
```bash
# Install ROS 2 Jazzy (same steps as RPi above)

# Install slam_toolbox and Nav2
sudo apt install ros-jazzy-slam-toolbox -y
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup -y

# Install homer_navigation
mkdir -p ~/homer_ws/src && cd ~/homer_ws/src
git clone https://github.com/linzhanguca/homer_navigation.git
cd ~/homer_ws
colcon build
echo "source ~/homer_ws/install/local_setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Network Configuration
Both the Raspberry Pi and server must be on the same network with matching ROS settings:
```bash
# Run on BOTH machines
echo "export ROS_DOMAIN_ID=85" >> ~/.bashrc
sudo apt install ros-jazzy-rmw-cyclonedds-cpp -y
echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc
source ~/.bashrc
```

### Starting Map Creation
```bash
# On Raspberry Pi:
ros2 launch homer_bringup homer_launch.py

# On Server (Terminal 1):
ros2 launch homer_navigation create_map.launch.py

# On Server (Terminal 2) - drive robot to build map:
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Saving the Map
In RViz, go to the **SlamToolboxPlugin** panel and use the Serialize Map button:
1. Type the absolute path in the text box next to "Serialize Map" (e.g. `/home/username/maps/P03`)
2. Click **Serialize Map**
3. Verify two files are created: `P03.data` and `P03.posegraph`

**CLI method (bonus):**
```bash
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '/home/username/maps/P03'}"
```

### Starting Autonomous Navigation
```bash
# Edit map path in localization config first:
nano ~/homer_ws/src/homer_navigation/configs/localization_params.yaml
# Set: map_file_name: /home/username/maps/P03

# Rebuild:
cd ~/homer_ws && colcon build && source ~/.bashrc

# On Raspberry Pi:
ros2 launch homer_bringup homer_launch.py

# On Server:
ros2 launch homer_navigation navigation.launch.py

# Run navigation node (on Raspberry Pi):
ros2 run wonklet navigate
```

---

## Navigation Node
The `wonklet` package contains the autonomous navigation node. It uses the **ROS 2 action client** to send a `NavigateToPose` goal to Nav2, which handles path planning and obstacle avoidance autonomously.

The map files for this project are located in the `/maps` directory:
- `P03.data`
- `P03.posegraph`

---

## License
MIT