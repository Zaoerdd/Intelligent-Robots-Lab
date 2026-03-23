#!/usr/bin/env python3
import math

import rospy
import tf2_ros
from geometry_msgs.msg import TransformStamped


if __name__ == '__main__':
    rospy.init_node('dynamic_tf2_broadcaster')
    broadcaster = tf2_ros.TransformBroadcaster()
    rate = rospy.Rate(10.0)

    while not rospy.is_shutdown():
        angle = rospy.Time.now().to_sec() * math.pi
        transform = TransformStamped()
        transform.header.stamp = rospy.Time.now()
        transform.header.frame_id = 'turtle1'
        transform.child_frame_id = 'carrot1'
        transform.transform.translation.x = 2.0 * math.sin(angle)
        transform.transform.translation.y = 2.0 * math.cos(angle)
        transform.transform.translation.z = 0.0
        transform.transform.rotation.x = 0.0
        transform.transform.rotation.y = 0.0
        transform.transform.rotation.z = 0.0
        transform.transform.rotation.w = 1.0
        broadcaster.sendTransform(transform)
        rate.sleep()
