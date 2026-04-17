#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-/home/ubuntu/lab6_capture}"
PIDS=()

cleanup() {
  set +e
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  pkill -f 'view_zaoer_bot_lab_world.launch' 2>/dev/null || true
  pkill -f 'spawn_zaoer_bot.launch' 2>/dev/null || true
  pkill -f 'rosmaster' 2>/dev/null || true
  pkill -f 'roscore' 2>/dev/null || true
  pkill -f 'gzserver' 2>/dev/null || true
  pkill -f 'gzclient' 2>/dev/null || true
  pkill -x rviz 2>/dev/null || true
  pkill -x Xvfb 2>/dev/null || true
  rm -f /tmp/.X99-lock 2>/dev/null || true
}

find_window_id() {
  local pattern="$1"
  DISPLAY=:99 xwininfo -root -tree | awk -v pat="$pattern" 'tolower($0) ~ tolower(pat) {print $1; exit}'
}

trap cleanup EXIT
cleanup

mkdir -p "$OUT_DIR"

source /opt/ros/noetic/setup.bash
source /home/ubuntu/catkin_ws/devel/setup.bash
export DISABLE_ROS1_EOL_WARNINGS=1

Xvfb :99 -screen 0 2200x1200x24 >/tmp/zaoer_bot_xvfb.log 2>&1 &
PIDS+=($!)
sleep 2

DISPLAY=:99 roslaunch zaoer_bot_gazebo view_zaoer_bot_lab_world.launch gui:=true rviz:=true >/tmp/zaoer_bot_demo.log 2>&1 &
PIDS+=($!)
sleep 35

gazebo_wid="$(find_window_id 'gazebo' || true)"
rviz_wid="$(find_window_id 'rviz' || true)"

if [[ -n "$gazebo_wid" ]]; then
  DISPLAY=:99 wmctrl -i -r "$gazebo_wid" -e 0,0,0,1100,1200 || true
fi

if [[ -n "$rviz_wid" ]]; then
  DISPLAY=:99 wmctrl -i -r "$rviz_wid" -e 0,1100,0,1100,1200 || true
fi

sleep 3

if [[ -n "$gazebo_wid" ]]; then
  DISPLAY=:99 import -window "$gazebo_wid" "$OUT_DIR/gazebo.png"
fi

if [[ -n "$rviz_wid" ]]; then
  DISPLAY=:99 import -window "$rviz_wid" "$OUT_DIR/rviz.png"
fi

DISPLAY=:99 import -window root "$OUT_DIR/desktop.png"

rostopic list | sort > "$OUT_DIR/topics.txt"
timeout 10s rostopic echo -n 1 /scan > "$OUT_DIR/scan_sample.txt" || true
timeout 10s rostopic echo -n 1 /camera/camera_info > "$OUT_DIR/camera_info.txt" || true
rosnode list | sort > "$OUT_DIR/nodes.txt"

for img in "$OUT_DIR"/*.png; do
  identify "$img"
done
