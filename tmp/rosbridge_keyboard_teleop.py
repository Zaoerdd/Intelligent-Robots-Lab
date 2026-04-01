import argparse
import msvcrt
import sys
import time

import roslibpy


HELP = """
ROSBridge keyboard teleop

Keys:
  w  forward
  s  backward
  a  turn left
  d  turn right
  space  stop
  q  quit
"""


def publish_twist(topic, linear_x: float, angular_z: float) -> None:
    topic.publish(
        roslibpy.Message(
            {
                "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": angular_z},
            }
        )
    )


def run_demo(topic) -> None:
    steps = [
        ("forward", 0.15, 0.0, 1.0),
        ("left", 0.0, 0.8, 1.0),
        ("stop", 0.0, 0.0, 0.5),
    ]
    for label, linear_x, angular_z, duration in steps:
        print(f"[demo] {label}: linear_x={linear_x:.2f} angular_z={angular_z:.2f}")
        publish_twist(topic, linear_x, angular_z)
        time.sleep(duration)
    publish_twist(topic, 0.0, 0.0)
    print("[demo] done")


def run_interactive(topic) -> None:
    print(HELP.strip())
    print("Waiting for keyboard input...")
    while True:
        key = msvcrt.getwch().lower()
        if key == "q":
            publish_twist(topic, 0.0, 0.0)
            print("quit")
            return
        if key == "w":
            publish_twist(topic, 0.15, 0.0)
            print("forward")
        elif key == "s":
            publish_twist(topic, -0.10, 0.0)
            print("backward")
        elif key == "a":
            publish_twist(topic, 0.0, 0.8)
            print("left")
        elif key == "d":
            publish_twist(topic, 0.0, -0.8)
            print("right")
        elif key == " ":
            publish_twist(topic, 0.0, 0.0)
            print("stop")


def main() -> int:
    parser = argparse.ArgumentParser(description="Keyboard teleop over rosbridge.")
    parser.add_argument("--host", default="192.168.40.128")
    parser.add_argument("--port", type=int, default=9090)
    parser.add_argument("--topic", default="/cmd_vel")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    client = roslibpy.Ros(host=args.host, port=args.port)
    client.run()
    if not client.is_connected:
        print("failed to connect")
        return 1

    topic = roslibpy.Topic(client, args.topic, "geometry_msgs/Twist")
    topic.advertise()
    try:
        if args.demo:
            run_demo(topic)
        else:
            run_interactive(topic)
    finally:
        publish_twist(topic, 0.0, 0.0)
        time.sleep(0.2)
        topic.unadvertise()
        client.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
