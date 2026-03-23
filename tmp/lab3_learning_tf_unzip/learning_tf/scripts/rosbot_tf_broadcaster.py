#!/usr/bin/env python3
import rospy
import tf
import tf2_ros
from geometry_msgs.msg import TransformStamped


if __name__ == '__main__':
    rospy.init_node('rosbot_tf_broadcaster')
    parent_frame = rospy.get_param('~parent_frame', 'base_link')
    child_frame = rospy.get_param('~child_frame', 'base_laser')
    x = float(rospy.get_param('~x', 0.1))
    y = float(rospy.get_param('~y', 0.0))
    z = float(rospy.get_param('~z', 0.2))
    roll = float(rospy.get_param('~roll', 0.0))
    pitch = float(rospy.get_param('~pitch', 0.0))
    yaw = float(rospy.get_param('~yaw', 0.0))

    quaternion = tf.transformations.quaternion_from_euler(roll, pitch, yaw)
    transform = TransformStamped()
    transform.header.stamp = rospy.Time.now()
    transform.header.frame_id = parent_frame
    transform.child_frame_id = child_frame
    transform.transform.translation.x = x
    transform.transform.translation.y = y
    transform.transform.translation.z = z
    transform.transform.rotation.x = quaternion[0]
    transform.transform.rotation.y = quaternion[1]
    transform.transform.rotation.z = quaternion[2]
    transform.transform.rotation.w = quaternion[3]

    broadcaster = tf2_ros.StaticTransformBroadcaster()
    broadcaster.sendTransform(transform)
    rospy.loginfo('Publishing static transform %s -> %s', parent_frame, child_frame)
    rospy.spin()
