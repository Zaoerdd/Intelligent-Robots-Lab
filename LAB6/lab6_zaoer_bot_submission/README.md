# Lab 6 Submission: Zaoer Bot

This submission contains a complete ROS Noetic catkin workspace source tree for Lab 6.

## Contents

- `catkin_ws/src/zaoer_bot_description`: self-inspired robot model in Xacro/URDF
- `catkin_ws/src/zaoer_bot_gazebo`: Gazebo world, launch files, RViz config, and capture script
- `report`: experiment report sources and generated assets

## Build And Run

```bash
cd ~/catkin_ws/src
cp -r /path/to/zaoer_bot_description /path/to/zaoer_bot_gazebo .
cd ~/catkin_ws
catkin_make
source devel/setup.bash
roslaunch zaoer_bot_gazebo view_zaoer_bot_lab_world.launch
```

## Automatic Screenshot Capture

```bash
cd ~/catkin_ws
source devel/setup.bash
bash src/zaoer_bot_gazebo/scripts/capture_lab6_results.sh ~/lab6_capture
```
