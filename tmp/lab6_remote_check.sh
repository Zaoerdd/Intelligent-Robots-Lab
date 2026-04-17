#!/usr/bin/env bash
set -euo pipefail

PID=""
XVFB_PID=""

cleanup() {
  set +e
  if [[ -n "${PID}" ]]; then
    kill "${PID}" 2>/dev/null || true
    wait "${PID}" 2>/dev/null || true
  fi
  if [[ -n "${XVFB_PID}" ]]; then
    kill "${XVFB_PID}" 2>/dev/null || true
    wait "${XVFB_PID}" 2>/dev/null || true
  fi
  pkill -f 'view_zaoer_bot_lab_world.launch' 2>/dev/null || true
  pkill -f 'spawn_zaoer_bot.launch' 2>/dev/null || true
  pkill -f 'rosmaster' 2>/dev/null || true
  pkill -f 'roscore' 2>/dev/null || true
  pkill -f 'gzserver' 2>/dev/null || true
  pkill -f 'gzclient' 2>/dev/null || true
  pkill -x Xvfb 2>/dev/null || true
  rm -f /tmp/.X99-lock 2>/dev/null || true
}

trap cleanup EXIT

source /opt/ros/noetic/setup.bash
source /home/ubuntu/catkin_ws/devel/setup.bash

rosrun xacro xacro "$(rospack find zaoer_bot_description)/urdf/zaoer_bot.urdf.xacro" >/tmp/zaoer_bot.urdf

Xvfb :99 -screen 0 1600x1000x24 >/tmp/zaoer_check_xvfb.log 2>&1 &
XVFB_PID="$!"
sleep 2

DISPLAY=:99 roslaunch zaoer_bot_gazebo view_zaoer_bot_lab_world.launch gui:=true rviz:=false >/tmp/zaoer_launch.log 2>&1 &
PID="$!"
sleep 28

echo "==== TOPICS ===="
rostopic list | sort | tee /tmp/zaoer_topics.txt
echo
echo "==== SCAN SAMPLE ===="
timeout 8s rostopic echo -n 1 /scan > /tmp/zaoer_scan.txt || true
sed -n '1,20p' /tmp/zaoer_scan.txt
echo
echo "==== CAMERA INFO SAMPLE ===="
timeout 8s rostopic echo -n 1 /camera/camera_info > /tmp/zaoer_camera_info.txt || true
sed -n '1,20p' /tmp/zaoer_camera_info.txt
