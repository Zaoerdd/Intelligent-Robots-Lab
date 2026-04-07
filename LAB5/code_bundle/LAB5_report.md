# CS401 Intelligent Robotics Lab 05 Report

Date: 2026-04-01

## 1. Objectives

This lab focused on the simulation of the `limo` vehicle in ROS Noetic and Gazebo. The main goals were:

1. Build and configure the `limo` simulation workspace.
2. Display the `limo` model in RViz and start the Ackerman-motion Gazebo simulation.
3. Understand different control methods, including `rqt_robot_steering` and keyboard teleoperation.
4. Run the demo pipeline for extrinsic camera calibration, lane detection, and lane-following control.

## 2. Environment

- Remote machine: `ubuntu@192.168.40.128`
- OS: Ubuntu 20.04
- ROS: Noetic
- Workspace: `~/limo_ws`
- Source repository: `ugv_gazebo_sim`

The workspace was created, dependencies were installed, and `catkin_make` completed successfully.

## 3. Validation Summary

The following items were verified during this session:

- Launch files resolved correctly for `display_models`, `limo_ackerman`, `limo_demo`, `extrinsic_camera_calibration`, `detect_lane`, and `turtlebot3_autorace_control_lane`.
- In the Ackerman simulation, `/cmd_vel`, `/limo/scan`, `/limo/color/image_raw`, `/limo/depth/image_raw`, `/limo/imu`, `/clock`, and `/tf` were available.
- In the lane-detection pipeline, `/camera/image_projected_compensated`, `/detect/image_lane/compressed`, `/detect/lane`, and `/cmd_vel` were active.
- `/detect/lane` published `std_msgs/Float64`, `/control_lane` subscribed to it, and `/cmd_vel` was published back to Gazebo.

See `lab5_validation_summary.txt` for the full validation details.

## 4. Workflow Figures

The report uses two kinds of figures:

- Reference figures copied from the provided `LAB5/README.md` images to document the intended RViz, Gazebo, and UI workflow.
- Live figures generated in this session from ROS topics, especially for the projected camera image and the lane-detection output.

## 5. Runtime Fix

During the live validation of `roslaunch limo_detect detect_lane.launch`, the original `detect_lane` node crashed with:

`AttributeError: 'DetectLane' object has no attribute 'mov_avg_left'`

To finish the lab pipeline, a minimal runtime fix was applied:

- Initialize the left/right lane-fit arrays.
- Initialize moving-average buffers for both lane histories.
- Guard the averaging step when history arrays are still empty.

The patched script is saved as `generated/detect_lane_fixed.py`.

## 6. Conclusion

Lab 5 was reproduced successfully on the remote Ubuntu machine. The `limo` workspace was built, the RViz/Gazebo launch chain was validated, and the lane-detection pipeline was brought up end-to-end. The final report PDF combines the provided reference images with live validation evidence and live ROS-generated result images from the current session.
