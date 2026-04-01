# LAB4 Screenshot Checklist

These five screenshots are the safest set to submit for Part 2, Part 3, and Part 4.

## 1. Part 2 simulation screenshot

Suggested filename: `part2_rviz_camera_lidar.png`

This screenshot should include all of the following:

- the RViz main window
- the `LaserScan` visualization in the main view
- the camera image panel or `Image` display in RViz
- preferably the left `Displays` panel showing both `LaserScan` and `Image`

## 2. Part 3 remote-machine screenshot

Suggested filename: `part3_remote_bringup.png`

This screenshot should include:

- an SSH session connected to `ubuntu@192.168.40.128`
- the terminal where TurtleBot bringup is running
- preferably `echo $ROS_MASTER_URI`
- preferably `rostopic list`

In the current setup, the remote side can show the Gazebo world, `turtlebot3_remote.launch`, and `rosbridge_websocket.launch`.

## 3. Part 3 local-machine screenshot

Suggested filename: `part3_local_teleop.png`

This screenshot should include:

- the local terminal running keyboard teleoperation
- a prompt such as `Reading from keyboard`
- preferably another terminal showing `rostopic echo -n 1 /cmd_vel`

In the current setup, the local command is:

`python tmp\rosbridge_keyboard_teleop.py --host 192.168.40.128`

## 4. Part 4 calibration-process screenshot

Suggested filename: `part4_calibration_process.png`

This screenshot should include:

- the `cameracalibrator.py` window
- detected chessboard corners
- the `X`, `Y`, `Size`, and `Skew` progress bars
- preferably the `CALIBRATE` button enabled

## 5. Part 4 calibration-parameter screenshot

Suggested filename: `part4_camera_parameters.png`

This screenshot should include:

- the saved `yaml` or `ost.txt` calibration file
- `camera_matrix`
- `distortion_coefficients`
- preferably `rectification_matrix`
- preferably `projection_matrix`

If no physical USB camera is attached to the VM, use the generated parameter file in `LAB4/generated/part4_camera_parameters.yaml` only as a placeholder and replace it with a real-camera screenshot before final submission if required by the teacher.

## Minimum required set

If the teacher only wants the minimum set, keep these four:

1. `part2_rviz_camera_lidar.png`
2. `part3_remote_bringup.png`
3. `part3_local_teleop.png`
4. `part4_camera_parameters.png`

Submitting all five is still recommended.
