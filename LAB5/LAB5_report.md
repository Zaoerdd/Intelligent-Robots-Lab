# CS401 Intelligent Robotics Lab 05 Report

Date: 2026-04-01

## 1. Objectives

This lab focused on simulation and perception for the `limo` vehicle in ROS Noetic. The main tasks were:

1. Build the `limo_ws` workspace and compile the simulation packages.
2. Display the LIMO model in RViz and run the Ackerman-mode simulation in Gazebo.
3. Review the common control methods for the simulated robot.
4. Run the camera projection, lane detection, and lane-following control pipeline.

## 2. Environment

- Remote machine: `ubuntu@192.168.40.128`
- Operating system: Ubuntu 20.04
- ROS version: Noetic
- Workspace: `~/limo_ws`
- Repository: `ugv_gazebo_sim`

The required packages were installed and the workspace was compiled successfully with `catkin_make`.

## 3. Build and Launch Commands

Main setup and runtime commands used in this lab:

```bash
mkdir -p ~/limo_ws/src
cd ~/limo_ws/src
git clone https://github.com/Intelligent-Robot-Course/ugv_gazebo_sim.git
cd ~/limo_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make

source /opt/ros/noetic/setup.bash
source ~/limo_ws/devel/setup.bash
roslaunch limo_description display_models.launch
roslaunch limo_gazebo_sim limo_ackerman.launch
roslaunch limo_gazebo_sim limo_demo.launch
roslaunch limo_camera extrinsic_camera_calibration.launch
roslaunch limo_detect detect_lane.launch
roslaunch limo_driving turtlebot3_autorace_control_lane.launch
```

The launch files were validated successfully during this session.

## 4. Results

### 4.1 RViz Model Display

The first step was to load the LIMO URDF model in RViz using `display_models.launch`. The screenshot below shows the robot model and the default RViz display configuration.

Figure: `generated/manual_model_display.png`

### 4.2 Ackerman Simulation in Gazebo

After the model was displayed successfully, the Ackerman simulation was started with `limo_ackerman.launch`. The screenshot below shows Gazebo and RViz running at the same time.

During runtime verification, the following ROS topics were confirmed:

- `/cmd_vel`
- `/limo/scan`
- `/limo/color/image_raw`
- `/limo/depth/image_raw`
- `/limo/imu`
- `/tf`

Figure: `generated/manual_ackerman_sim.png`

### 4.3 Control Methods

The lab material introduced two basic control methods:

```bash
rosrun rqt_robot_steering rqt_robot_steering
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

These commands provide GUI-based and keyboard-based motion control for the simulated robot.

### 4.4 Camera Projection and Extrinsic Calibration

The camera calibration pipeline was launched with `extrinsic_camera_calibration.launch`. The projected ground-view image was observed through `rqt Image View`, and the screenshot below shows the projected topic display.

Verified topic:

- `/camera/image_projected_compensated`

Figure: `generated/manual_projected_view.png`

### 4.5 Lane Detection and Lane-Following Control

The lane-detection pipeline was started with `detect_lane.launch`, and the controller was started with `turtlebot3_autorace_control_lane.launch`. The screenshot below shows the detected lane image in `rqt Image View`.

Verified topic chain:

- `/camera/image_projected_compensated`
- `/detect/image_lane/compressed`
- `/detect/lane`
- `/cmd_vel`

Runtime checks confirmed:

- `/detect/lane` published `std_msgs/Float64`
- `/control_lane` subscribed to `/detect/lane`
- `/cmd_vel` was published by `/control_lane`
- `/gazebo` subscribed to `/cmd_vel`

Figure: `generated/manual_detect_lane.png`

## 5. Runtime Fix

During the first live run of `detect_lane.launch`, the original node crashed with:

`AttributeError: 'DetectLane' object has no attribute 'mov_avg_left'`

To complete the pipeline, a minimal fix was applied:

- Initialize left and right lane-fit state arrays.
- Initialize moving-average buffers.
- Guard the averaging step when the history arrays are still empty.

The patched file is saved as:

- `generated/detect_lane_fixed.py`

After applying this fix, the lane-detection and lane-following nodes ran successfully and the topic chain remained active.

## 6. Conclusion

Lab 5 was completed successfully on the remote Ubuntu machine. The LIMO model was displayed in RViz, Ackerman-mode simulation was started in Gazebo, the projected camera view was verified, and the lane-detection pipeline was brought up end-to-end. The final report uses manually captured screenshots from the actual experiment and includes the runtime validation and code fix needed to keep the demo pipeline running.
