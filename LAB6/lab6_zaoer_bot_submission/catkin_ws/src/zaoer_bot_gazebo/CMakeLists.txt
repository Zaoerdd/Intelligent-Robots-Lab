cmake_minimum_required(VERSION 3.0.2)
project(zaoer_bot_gazebo)

find_package(catkin REQUIRED COMPONENTS
  gazebo_plugins
  gazebo_ros
  robot_state_publisher
  roscpp
  rospy
  rviz
  xacro
  zaoer_bot_description
)

catkin_package()

install(DIRECTORY launch rviz worlds
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(PROGRAMS scripts/capture_lab6_results.sh
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
