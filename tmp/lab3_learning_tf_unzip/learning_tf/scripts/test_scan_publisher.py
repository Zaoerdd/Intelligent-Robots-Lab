#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan


if __name__ == '__main__':
    rospy.init_node('test_scan_publisher')
    scan_topic = rospy.get_param('~scan_topic', '/scan')
    frame_id = rospy.get_param('~frame_id', 'base_laser')
    rate_hz = float(rospy.get_param('~rate', 5.0))
    publisher = rospy.Publisher(scan_topic, LaserScan, queue_size=1)
    rate = rospy.Rate(rate_hz)

    angle_min = -0.2
    angle_increment = 0.1
    ranges = [0.45, 0.40, 0.30, 0.40, 0.45]

    while not rospy.is_shutdown():
        msg = LaserScan()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = frame_id
        msg.angle_min = angle_min
        msg.angle_max = angle_min + angle_increment * (len(ranges) - 1)
        msg.angle_increment = angle_increment
        msg.time_increment = 0.0
        msg.scan_time = 1.0 / rate_hz
        msg.range_min = 0.0
        msg.range_max = 10.0
        msg.ranges = list(ranges)
        msg.intensities = [1.0] * len(ranges)
        publisher.publish(msg)
        rate.sleep()
