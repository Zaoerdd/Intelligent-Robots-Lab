#!/usr/bin/env python3
import math

import rospy
import tf2_ros
import turtlesim.srv
from geometry_msgs.msg import Twist


def spawn_turtle(name):
    rospy.wait_for_service('spawn')
    spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
    try:
        spawner(4.0, 2.0, 0.0, name)
    except rospy.ServiceException as exc:
        if 'already exists' not in str(exc):
            raise


if __name__ == '__main__':
    rospy.init_node('turtle_tf2_listener')
    turtle_name = rospy.get_param('~turtle', 'turtle2')
    target_frame = rospy.get_param('~target_frame', 'turtle1')

    tf_buffer = tf2_ros.Buffer()
    tf2_ros.TransformListener(tf_buffer)

    spawn_turtle(turtle_name)
    publisher = rospy.Publisher(f'/{turtle_name}/cmd_vel', Twist, queue_size=1)
    rate = rospy.Rate(10.0)

    while not rospy.is_shutdown():
        try:
            transform = tf_buffer.lookup_transform(turtle_name, target_frame, rospy.Time(0), rospy.Duration(1.0))
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            rate.sleep()
            continue

        msg = Twist()
        msg.angular.z = 4.0 * math.atan2(
            transform.transform.translation.y,
            transform.transform.translation.x,
        )
        msg.linear.x = 0.5 * math.sqrt(
            transform.transform.translation.x ** 2 + transform.transform.translation.y ** 2
        )
        publisher.publish(msg)
        rate.sleep()
