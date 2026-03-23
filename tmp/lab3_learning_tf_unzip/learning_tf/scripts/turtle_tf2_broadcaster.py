#!/usr/bin/env python3
import rospy
import tf
import tf2_ros
import turtlesim.msg
from geometry_msgs.msg import TransformStamped


class TurtleTFBroadcaster:
    def __init__(self, turtle_name):
        self.turtle_name = turtle_name
        self.broadcaster = tf2_ros.TransformBroadcaster()
        self.subscriber = rospy.Subscriber(
            f'/{turtle_name}/pose',
            turtlesim.msg.Pose,
            self.handle_pose,
            queue_size=10,
        )

    def handle_pose(self, msg):
        transform = TransformStamped()
        transform.header.stamp = rospy.Time.now()
        transform.header.frame_id = 'world'
        transform.child_frame_id = self.turtle_name
        transform.transform.translation.x = msg.x
        transform.transform.translation.y = msg.y
        transform.transform.translation.z = 0.0

        quaternion = tf.transformations.quaternion_from_euler(0.0, 0.0, msg.theta)
        transform.transform.rotation.x = quaternion[0]
        transform.transform.rotation.y = quaternion[1]
        transform.transform.rotation.z = quaternion[2]
        transform.transform.rotation.w = quaternion[3]
        self.broadcaster.sendTransform(transform)


if __name__ == '__main__':
    rospy.init_node('turtle_tf2_broadcaster')
    TurtleTFBroadcaster(rospy.get_param('~turtle'))
    rospy.spin()
