#!/usr/bin/env python3
import rospy
import turtlesim.msg
import turtlesim.srv
from geometry_msgs.msg import Point, PointStamped, Twist
from std_msgs.msg import Header


class PointPublisher:
    def __init__(self, turtle_name):
        self.publisher = rospy.Publisher('turtle_point_stamped', PointStamped, queue_size=1)
        self.subscriber = rospy.Subscriber(
            f'/{turtle_name}/pose',
            turtlesim.msg.Pose,
            self.handle_turtle_pose,
            queue_size=10,
        )

    def handle_turtle_pose(self, msg):
        point = PointStamped(
            header=Header(stamp=rospy.Time.now(), frame_id='world'),
            point=Point(msg.x, msg.y, 0.0),
        )
        self.publisher.publish(point)


if __name__ == '__main__':
    rospy.init_node('turtle_tf2_message_broadcaster')
    rospy.wait_for_service('spawn')
    spawner = rospy.ServiceProxy('spawn', turtlesim.srv.Spawn)
    turtle_name = rospy.get_param('~turtle', 'turtle3')
    try:
        spawner(4.0, 2.0, 0.0, turtle_name)
    except rospy.ServiceException as exc:
        if 'already exists' not in str(exc):
            raise

    PointPublisher(turtle_name)
    publisher = rospy.Publisher(f'/{turtle_name}/cmd_vel', Twist, queue_size=1)
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        msg = Twist()
        msg.linear.x = 1.0
        msg.angular.z = 1.0
        publisher.publish(msg)
        rate.sleep()
