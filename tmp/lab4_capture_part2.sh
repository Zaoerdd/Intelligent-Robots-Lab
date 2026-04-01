#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-/home/ubuntu/part2_rviz_camera_lidar.png}"
RVIZ_CFG="/home/ubuntu/lab4_turtlebot3_camera.rviz"
PIDS=()

cleanup() {
  set +e
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  pkill -f 'roslaunch turtlebot3_gazebo turtlebot3_world.launch' 2>/dev/null || true
  pkill -f 'roslaunch turtlebot3_gazebo turtlebot3_simulation.launch' 2>/dev/null || true
  pkill -f 'rviz -d /home/ubuntu/lab4_turtlebot3_camera.rviz' 2>/dev/null || true
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

source /opt/ros/noetic/setup.bash
source /home/ubuntu/catkin_ws/devel/setup.bash 2>/dev/null || true

export TURTLEBOT3_MODEL=waffle

python3 - <<'PY'
from pathlib import Path
src = Path("/opt/ros/noetic/share/turtlebot3_gazebo/rviz/turtlebot3_gazebo_model.rviz")
dst = Path("/home/ubuntu/lab4_turtlebot3_camera.rviz")
text = src.read_text()
text = text.replace("- Class: rviz/Camera\n      Enabled: false", "- Class: rviz/Camera\n      Enabled: true", 1)
dst.write_text(text)
PY

Xvfb :99 -screen 0 1600x1000x24 >/tmp/lab4_xvfb.log 2>&1 &
PIDS+=($!)
sleep 2

DISPLAY=:99 roslaunch turtlebot3_gazebo turtlebot3_world.launch >/tmp/lab4_part2_world.log 2>&1 &
PIDS+=($!)
sleep 25

DISPLAY=:99 roslaunch turtlebot3_gazebo turtlebot3_simulation.launch >/tmp/lab4_part2_simulation.log 2>&1 &
PIDS+=($!)
sleep 12

DISPLAY=:99 rviz -d "$RVIZ_CFG" >/tmp/lab4_part2_rviz.log 2>&1 &
PIDS+=($!)
sleep 18

wid="$(find_window_id 'rviz' || true)"
if [[ -n "$wid" ]]; then
  DISPLAY=:99 wmctrl -i -r "$wid" -e 0,0,0,1600,1000 || true
  sleep 2
  DISPLAY=:99 import -window "$wid" "$OUT"
else
  DISPLAY=:99 import -window root "$OUT"
fi

identify "$OUT"
