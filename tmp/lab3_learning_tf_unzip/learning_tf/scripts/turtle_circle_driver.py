#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist


if __name__ == '__main__':
    rospy.init_node('turtle_circle_driver')
    turtle_name = rospy.get_param('~turtle', 'turtle1')
    linear = float(rospy.get_param('~linear', 1.0))
    angular = float(rospy.get_param('~angular', 0.8))
    publisher = rospy.Publisher(f'/{turtle_name}/cmd_vel', Twist, queue_size=1)
    rate = rospy.Rate(10.0)

    while not rospy.is_shutdown():
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        publisher.publish(msg)
        rate.sleep()
