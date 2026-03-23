#!/usr/bin/env python3
import rospy
import tf2_ros
from laser_geometry import LaserProjection
from sensor_msgs.msg import LaserScan, PointCloud2
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud


class RobotTFListener:
    def __init__(self):
        self.target_frame = rospy.get_param('~target_frame', 'base_link')
        self.scan_topic = rospy.get_param('~scan_topic', '/scan')
        self.output_topic = rospy.get_param('~output_topic', '/scan_in_base_link')
        self.projector = LaserProjection()
        self.tf_buffer = tf2_ros.Buffer(cache_time=rospy.Duration(30.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.publisher = rospy.Publisher(self.output_topic, PointCloud2, queue_size=1)
        self.subscriber = rospy.Subscriber(self.scan_topic, LaserScan, self.handle_scan, queue_size=10)
        rospy.loginfo('Transforming %s into %s and publishing %s', self.scan_topic, self.target_frame, self.output_topic)

    def handle_scan(self, scan_msg):
        source_frame = scan_msg.header.frame_id or 'base_laser'
        lookup_time = scan_msg.header.stamp if scan_msg.header.stamp != rospy.Time() else rospy.Time(0)
        try:
            transform = self.tf_buffer.lookup_transform(
                self.target_frame,
                source_frame,
                lookup_time,
                rospy.Duration(1.0),
            )
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as exc:
            rospy.logwarn_throttle(2.0, 'TF lookup failed for %s -> %s: %s', source_frame, self.target_frame, exc)
            return

        cloud = self.projector.projectLaser(scan_msg)
        transformed_cloud = do_transform_cloud(cloud, transform)
        transformed_cloud.header.frame_id = self.target_frame
        transformed_cloud.header.stamp = scan_msg.header.stamp
        self.publisher.publish(transformed_cloud)


if __name__ == '__main__':
    rospy.init_node('robot_tf_listener')
    RobotTFListener()
    rospy.spin()
