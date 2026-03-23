cmake_minimum_required(VERSION 3.0.2)
project(learning_tf)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  laser_geometry
  roscpp
  rospy
  sensor_msgs
  std_msgs
  tf
  tf2
  tf2_geometry_msgs
  tf2_ros
  tf2_sensor_msgs
  turtlesim
)

catkin_package(
  CATKIN_DEPENDS
    geometry_msgs
    laser_geometry
    roscpp
    rospy
    sensor_msgs
    std_msgs
    tf
    tf2
    tf2_geometry_msgs
    tf2_ros
    tf2_sensor_msgs
    turtlesim
)

catkin_install_python(PROGRAMS
  scripts/dynamic_tf2_broadcaster.py
  scripts/fixed_tf2_broadcaster.py
  scripts/robot_tf_listener.py
  scripts/rosbot_tf_broadcaster.py
  scripts/test_scan_publisher.py
  scripts/turtle_circle_driver.py
  scripts/turtle_tf2_broadcaster.py
  scripts/turtle_tf2_listener.py
  scripts/turtle_tf2_message_broadcaster.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
