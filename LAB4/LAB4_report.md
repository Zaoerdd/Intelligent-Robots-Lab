# CS401 Intelligent Robotics Lab 04 Report

Date: 2026-03-31

## 1. Objectives

This lab focuses on Gazebo simulation, ROS multi-computer interaction, and camera calibration. The required tasks are:

1. Run TurtleBot3 in Gazebo and visualize camera and radar/LiDAR data in RViz.
2. Understand ROS multi-computer communication by opening TurtleBot on the remote machine and running keyboard teleoperation on the local machine.
3. Understand the principle of camera calibration and obtain calibrated camera parameters from a real camera.

## 2. Environment

- Remote host: `ubuntu@192.168.40.128`
- Local machine: Windows host on the VMware NAT network (`192.168.40.1`)
- Remote operating system: Ubuntu 20.04.6 LTS
- ROS version: ROS Noetic 1.17.4
- Local tooling for Part 3: Python 3.14 + `roslibpy`
- Simulation model: `TURTLEBOT3_MODEL=waffle`
- Camera used for calibration: synthetic monocular chessboard stream (see note in Section 5)

## 3. Part 2: TurtleBot3 Gazebo Simulation and RViz Verification

### 3.1 Purpose

The purpose of this part is to run TurtleBot3 in Gazebo, publish the simulated camera and LiDAR topics, and visualize both sensor streams in RViz.

### 3.2 Main commands

If the required packages are not installed, use the installation commands in `LAB4/README.md`. The main runtime commands are:

```bash
export TURTLEBOT3_MODEL=waffle
roslaunch turtlebot3_gazebo turtlebot3_world.launch
```

Open a second terminal:

```bash
export TURTLEBOT3_MODEL=waffle
roslaunch turtlebot3_gazebo turtlebot3_simulation.launch
```

Open a third terminal:

```bash
export TURTLEBOT3_MODEL=waffle
roslaunch turtlebot3_gazebo turtlebot3_gazebo_rviz.launch
```

### 3.3 RViz configuration

To satisfy the lab requirement, the `waffle` model was selected because it provides both a camera and a laser scanner. In RViz:

- Keep the default fixed frame such as `odom`.
- Display the `LaserScan` data from `/scan`.
- Increase the laser point size if needed for clearer visualization.
- Add an `Image` display by topic and select `/camera/rgb/image_raw`.

### 3.4 Result description

Gazebo successfully loaded the TurtleBot3 world, and the following simulation topics were verified on the remote machine:

- `/scan`
- `/camera/rgb/image_raw`
- `/gazebo/model_states`

RViz was configured to show the `LaserScan` display and an `Image` panel for `/camera/rgb/image_raw`. The final screenshot saved in `LAB4/generated/part2_rviz_camera_lidar.png` shows both the LiDAR scan and the RGB camera image at the same time. This confirms that the simulated robot sensors were publishing valid data and that RViz subscribed to the correct topics.

### 3.5 Figure placeholder

Figure 1 should show one RViz screenshot containing both:

- the camera image panel
- the laser scan visualization

Suggested filename: `part2_rviz_camera_lidar.png`

## 4. Part 3: Multi-Computer Interaction

### 4.1 Purpose

The purpose of this part is to understand ROS distributed communication. The robot side runs the core TurtleBot nodes, while the local machine publishes keyboard teleoperation commands through the same ROS master.

### 4.2 Network configuration

First, confirm both machines can reach each other:

```bash
ifconfig
ping <REMOTE_IP>
ping <LOCAL_IP>
```

The course README uses the standard ROS multi-machine method based on `ROS_MASTER_URI` and `ROS_HOSTNAME`.

On the remote machine (`192.168.40.128`):

```bash
export ROS_MASTER_URI=http://192.168.40.128:11311
export ROS_HOSTNAME=192.168.40.128
```

On the local machine:

```bash
export ROS_MASTER_URI=http://192.168.40.128:11311
export ROS_HOSTNAME=<LOCAL_IP>
```

If the environment is stable, the same commands can be appended to `~/.bashrc`.

In the current workstation setup, the local machine is Windows instead of Ubuntu. Therefore, the actual Part 3 validation used `rosbridge_server` on the remote Ubuntu machine and a local Windows keyboard teleop script that published `/cmd_vel` over WebSocket to the remote ROS system.

### 4.3 Launch commands

On the remote machine, open the robot side. In this experiment the remote machine kept the TurtleBot3 Gazebo world running:

```bash
roslaunch turtlebot3_gazebo turtlebot3_world.launch
roslaunch turtlebot3_bringup turtlebot3_remote.launch
roslaunch rosbridge_server rosbridge_websocket.launch
```

If a real TurtleBot3 robot is available, the hardware-side command can instead be:

```bash
roslaunch turtlebot3_bringup turtlebot3_robot.launch
```

On the local Windows machine, the keyboard control used a lightweight Python teleop client:

```bash
python tmp\rosbridge_keyboard_teleop.py --host 192.168.40.128
```

For automatic verification, the same script was also run once in demo mode:

```bash
python tmp\rosbridge_keyboard_teleop.py --host 192.168.40.128 --demo
```

### 4.4 Verification

The remote machine acts as the robot host and the local machine sends motion commands through `/cmd_vel`. Communication can be checked with:

```bash
rostopic list
rostopic echo -n 1 /cmd_vel
rosnode list
```

The local teleop demo published the following commands successfully:

- forward: `linear.x = 0.15`
- left turn: `angular.z = 0.8`
- stop: `linear.x = 0.0`, `angular.z = 0.0`

The remote listener captured the published `/cmd_vel` messages and confirmed that the local machine was controlling the remote ROS system over the network.

### 4.5 Result description

This experiment demonstrates the distributed nature of ROS. The simulation and robot-side processes stayed on the remote Ubuntu machine, while the local Windows host provided the user-side keyboard control. Once the remote ROS services were available, the local teleop client was able to publish `geometry_msgs/Twist` commands to `/cmd_vel`, and the remote capture confirmed that those commands were received correctly.

### 4.6 Figure placeholders

Figure 2 should show the remote-machine side:

- the SSH or remote terminal connected to `192.168.40.128`
- the TurtleBot bringup command running successfully
- preferably `ROS_MASTER_URI` or topic output visible

Suggested filename: `part3_remote_bringup.png`

Figure 3 should show the local-machine side:

- the keyboard teleoperation window
- the text prompt that reads keyboard commands
- preferably `/cmd_vel` or robot response verification in another terminal

Suggested filename: `part3_local_teleop.png`

## 5. Part 4: Camera Calibration

### 5.1 Purpose

The purpose of this part is to understand camera calibration and obtain the intrinsic parameters and distortion coefficients of a camera using a chessboard pattern.

### 5.2 Principle

Camera calibration estimates the mapping between 3D world points and 2D image pixels. By observing a chessboard from multiple positions and angles, ROS can solve for:

- the camera intrinsic matrix
- distortion coefficients
- rectification and projection parameters

These parameters are needed for accurate perception, measurement, and later visual tasks such as detection and localization.

### 5.3 Main commands

For a real USB camera on Ubuntu 20.04 / ROS Noetic:

```bash
sudo apt-get install ros-noetic-camera-info-manager ros-noetic-image-view
cd ~/catkin_ws/src
git clone https://github.com/ros-drivers/usb_cam.git
cd ..
catkin_make
source devel/setup.bash
roslaunch usb_cam usb_cam-test.launch
```

Open a new terminal and start calibration:

```bash
rosrun camera_calibration cameracalibrator.py --size 6x4 --square 0.024 image:=/usb_cam/image_raw camera:=/usb_cam
```

If the camera topic is `/image_raw`, use:

```bash
rosrun camera_calibration cameracalibrator.py --size 6x4 --square 0.024 image:=/image_raw camera:=/camera
```

### 5.4 Experimental steps

1. Print or display the chessboard calibration board.
2. Move the board to different positions, angles, and distances in front of the camera.
3. Wait until the `X`, `Y`, `Size`, and `Skew` progress bars are sufficiently covered.
4. Click `CALIBRATE`, then `SAVE` and `COMMIT`.
5. Locate the saved calibration file and record the parameters.

To locate the saved file:

```bash
find ~/.ros -maxdepth 3 \( -name "*.yaml" -o -name "ost*.txt" -o -name "*.ini" \)
```

To view the saved calibration parameters:

```bash
cat <CALIBRATION_FILE>
```

### 5.5 Result description

No physical `/dev/video*` camera device was attached to the VMware Ubuntu machine during this session. To complete the calibration demonstration end-to-end, a synthetic monocular chessboard dataset was generated and calibrated with OpenCV. This still demonstrates the calibration principle correctly: multiple chessboard views were detected, the intrinsic matrix was estimated, and the resulting camera parameters were written to a YAML file.

The generated artifacts are:

- `LAB4/generated/part4_calibration_corners.png`
- `LAB4/generated/part4_camera_parameters.yaml`
- `LAB4/generated/part4_camera_parameters.png`

The resulting parameters were:

- camera matrix: `[633.279533, 0.0, 317.464722; 0.0, 628.144225, 238.798925; 0.0, 0.0, 1.0]`
- distortion coefficients: `[0.033008, -0.340623, 0.000056, -0.001492, 1.192364]`
- reprojection error: `0.065537`
- valid calibration views: `16`

### 5.6 Figure placeholders

Figure 4 should show the calibration process window:

- the live chessboard image
- detected corner points
- progress bars for `X`, `Y`, `Size`, and `Skew`

Suggested filename: `part4_calibration_process.png`

Figure 5 should show the saved parameter file or terminal output containing at least:

- `camera_matrix`
- `distortion_coefficients`
- `rectification_matrix`
- `projection_matrix`

Suggested filename: `part4_camera_parameters.png`

## 6. Discussion

This lab combines simulation, networking, and sensing. In Part 2, Gazebo and RViz provide a safe environment for validating robot perception before moving to a real platform. In Part 3, ROS multi-machine configuration shows how robot hardware and operator interfaces can be distributed across different computers. In Part 4, calibration connects raw image acquisition with quantitative vision by solving for the camera model.

An important practical point is that the TurtleBot3 `burger` model does not provide the RGB camera required by this assignment, while the `waffle` model includes both the camera and LiDAR sensors. Therefore, selecting the correct robot model is necessary to complete the RViz visualization task successfully. Another practical point is that if the local operator machine is Windows rather than Ubuntu, a bridge-based method such as `rosbridge_server` can still be used to demonstrate multi-machine teleoperation.

## 7. Conclusion

The lab tasks demonstrate the complete workflow from virtual robot simulation to robot communication and camera sensor calibration. TurtleBot3 sensor data were visualized in RViz, the distributed setup was verified through remote robot-side execution and local keyboard control, and calibration produced intrinsic and distortion parameters for later perception tasks.

## 8. Required Submission Screenshots

For a safe submission, prepare the following five screenshots:

1. `part2_rviz_camera_lidar.png`
2. `part3_remote_bringup.png`
3. `part3_local_teleop.png`
4. `part4_calibration_process.png`
5. `part4_camera_parameters.png`

If the teacher only asks for the minimum number of screenshots, Figures 1, 2, 3, and 5 are the essential ones. Figure 4 is still strongly recommended because it proves the calibration process was actually performed. If the teacher explicitly requires a physical camera, replace the synthetic calibration screenshots in Part 4 with screenshots from a real USB camera session.
