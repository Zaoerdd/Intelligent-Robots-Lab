#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import numpy as np
import cv2
from cv_bridge import CvBridge
from std_msgs.msg import UInt8, Float64
from sensor_msgs.msg import Image, CompressedImage
from dynamic_reconfigure.server import Server
from limo_detect.cfg import DetectLaneParamsConfig


class DetectLane:
    def __init__(self):
        self.hue_white_l = rospy.get_param("~detect/lane/white/hue_l", 0)
        self.hue_white_h = rospy.get_param("~detect/lane/white/hue_h", 179)
        self.saturation_white_l = rospy.get_param("~detect/lane/white/saturation_l", 0)
        self.saturation_white_h = rospy.get_param("~detect/lane/white/saturation_h", 70)
        self.lightness_white_l = rospy.get_param("~detect/lane/white/lightness_l", 105)
        self.lightness_white_h = rospy.get_param("~detect/lane/white/lightness_h", 255)

        self.hue_yellow_l = rospy.get_param("~detect/lane/yellow/hue_l", 10)
        self.hue_yellow_h = rospy.get_param("~detect/lane/yellow/hue_h", 127)
        self.saturation_yellow_l = rospy.get_param("~detect/lane/yellow/saturation_l", 70)
        self.saturation_yellow_h = rospy.get_param("~detect/lane/yellow/saturation_h", 255)
        self.lightness_yellow_l = rospy.get_param("~detect/lane/yellow/lightness_l", 95)
        self.lightness_yellow_h = rospy.get_param("~detect/lane/yellow/lightness_h", 255)

        self.is_calibration_mode = rospy.get_param("~is_detection_calibration_mode", False)
        if self.is_calibration_mode:
            Server(DetectLaneParamsConfig, self.cbGetDetectLaneParam)

        self.sub_image_type = "raw"
        self.pub_image_type = "compressed"

        if self.sub_image_type == "compressed":
            self.sub_image_original = rospy.Subscriber(
                "/detect/image_input/compressed", CompressedImage, self.cbFindLane, queue_size=1
            )
        else:
            self.sub_image_original = rospy.Subscriber(
                "/detect/image_input", Image, self.cbFindLane, queue_size=1
            )

        if self.pub_image_type == "compressed":
            self.pub_image_lane = rospy.Publisher("/detect/image_output/compressed", CompressedImage, queue_size=1)
        else:
            self.pub_image_lane = rospy.Publisher("/detect/image_output", Image, queue_size=1)

        if self.is_calibration_mode:
            if self.pub_image_type == "compressed":
                self.pub_image_white_lane = rospy.Publisher(
                    "/detect/image_output_sub1/compressed", CompressedImage, queue_size=1
                )
                self.pub_image_yellow_lane = rospy.Publisher(
                    "/detect/image_output_sub2/compressed", CompressedImage, queue_size=1
                )
            else:
                self.pub_image_white_lane = rospy.Publisher("/detect/image_output_sub1", Image, queue_size=1)
                self.pub_image_yellow_lane = rospy.Publisher("/detect/image_output_sub2", Image, queue_size=1)

        self.pub_lane = rospy.Publisher("/detect/lane", Float64, queue_size=1)
        self.pub_yellow_line_reliability = rospy.Publisher("/detect/yellow_line_reliability", UInt8, queue_size=1)
        self.pub_white_line_reliability = rospy.Publisher("/detect/white_line_reliability", UInt8, queue_size=1)

        self.cvBridge = CvBridge()
        self.counter = 1
        self.window_width = 1000.0
        self.window_height = 600.0
        self.reliability_white_line = 100
        self.reliability_yellow_line = 100

        # Added to prevent empty-history crashes during the first callbacks.
        self.left_fit = np.array([0.0, 0.0, 0.0])
        self.right_fit = np.array([0.0, 0.0, 0.0])
        self.left_fitx = np.zeros(int(self.window_height))
        self.right_fitx = np.zeros(int(self.window_height))
        self.mov_avg_left = np.empty((0, 3))
        self.mov_avg_right = np.empty((0, 3))
        self.lane_fit_bef = np.array([0.0, 0.0, 0.0])

    def cbGetDetectLaneParam(self, config, level):
        self.hue_white_l = config.hue_white_l
        self.hue_white_h = config.hue_white_h
        self.saturation_white_l = config.saturation_white_l
        self.saturation_white_h = config.saturation_white_h
        self.lightness_white_l = config.lightness_white_l
        self.lightness_white_h = config.lightness_white_h

        self.hue_yellow_l = config.hue_yellow_l
        self.hue_yellow_h = config.hue_yellow_h
        self.saturation_yellow_l = config.saturation_yellow_l
        self.saturation_yellow_h = config.saturation_yellow_h
        self.lightness_yellow_l = config.lightness_yellow_l
        self.lightness_yellow_h = config.lightness_yellow_h
        return config

    def cbFindLane(self, image_msg):
        if self.counter % 3 != 0:
            self.counter += 1
            return
        self.counter = 1

        if self.sub_image_type == "compressed":
            np_arr = np.frombuffer(image_msg.data, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        else:
            cv_image = self.cvBridge.imgmsg_to_cv2(image_msg, "bgr8")

        white_fraction, cv_white_lane = self.maskWhiteLane(cv_image)
        yellow_fraction, cv_yellow_lane = self.maskYellowLane(cv_image)

        try:
            if yellow_fraction > 3000:
                self.left_fitx, self.left_fit = self.fit_from_lines(self.left_fit, cv_yellow_lane)
                self.mov_avg_left = np.append(self.mov_avg_left, np.array([self.left_fit]), axis=0)
            if white_fraction > 3000:
                self.right_fitx, self.right_fit = self.fit_from_lines(self.right_fit, cv_white_lane)
                self.mov_avg_right = np.append(self.mov_avg_right, np.array([self.right_fit]), axis=0)
        except Exception:
            if yellow_fraction > 3000:
                self.left_fitx, self.left_fit = self.sliding_windown(cv_yellow_lane, "left")
                self.mov_avg_left = np.array([self.left_fit])
            if white_fraction > 3000:
                self.right_fitx, self.right_fit = self.sliding_windown(cv_white_lane, "right")
                self.mov_avg_right = np.array([self.right_fit])

        mov_avg_length = 5
        if self.mov_avg_left.shape[0] > 0:
            self.left_fit = np.array(
                [
                    np.mean(self.mov_avg_left[::-1][:, 0][0:mov_avg_length]),
                    np.mean(self.mov_avg_left[::-1][:, 1][0:mov_avg_length]),
                    np.mean(self.mov_avg_left[::-1][:, 2][0:mov_avg_length]),
                ]
            )
        if self.mov_avg_right.shape[0] > 0:
            self.right_fit = np.array(
                [
                    np.mean(self.mov_avg_right[::-1][:, 0][0:mov_avg_length]),
                    np.mean(self.mov_avg_right[::-1][:, 1][0:mov_avg_length]),
                    np.mean(self.mov_avg_right[::-1][:, 2][0:mov_avg_length]),
                ]
            )

        if self.mov_avg_left.shape[0] > 1000:
            self.mov_avg_left = self.mov_avg_left[0:mov_avg_length]
        if self.mov_avg_right.shape[0] > 1000:
            self.mov_avg_right = self.mov_avg_right[0:mov_avg_length]

        self.make_lane(cv_image, white_fraction, yellow_fraction)

    def maskWhiteLane(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_white = np.array([self.hue_white_l, self.saturation_white_l, self.lightness_white_l])
        upper_white = np.array([self.hue_white_h, self.saturation_white_h, self.lightness_white_h])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        fraction_num = np.count_nonzero(mask)

        if not self.is_calibration_mode:
            if fraction_num > 35000 and self.lightness_white_l < 250:
                self.lightness_white_l += 5
            elif fraction_num < 5000 and self.lightness_white_l > 50:
                self.lightness_white_l -= 5

        how_much_short = 600 - sum(np.count_nonzero(mask[i, ::]) > 0 for i in range(0, 600))
        if how_much_short > 100 and self.reliability_white_line >= 5:
            self.reliability_white_line -= 5
        elif how_much_short <= 100 and self.reliability_white_line <= 99:
            self.reliability_white_line += 5

        msg = UInt8()
        msg.data = self.reliability_white_line
        self.pub_white_line_reliability.publish(msg)

        if self.is_calibration_mode:
            if self.pub_image_type == "compressed":
                self.pub_image_white_lane.publish(self.cvBridge.cv2_to_compressed_imgmsg(mask, "jpg"))
            else:
                self.pub_image_white_lane.publish(self.cvBridge.cv2_to_imgmsg(mask, "bgr8"))

        return fraction_num, mask

    def maskYellowLane(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([self.hue_yellow_l, self.saturation_yellow_l, self.lightness_yellow_l])
        upper_yellow = np.array([self.hue_yellow_h, self.saturation_yellow_h, self.lightness_yellow_h])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        fraction_num = np.count_nonzero(mask)

        if not self.is_calibration_mode:
            if fraction_num > 35000 and self.lightness_yellow_l < 250:
                self.lightness_yellow_l += 20
            elif fraction_num < 5000 and self.lightness_yellow_l > 90:
                self.lightness_yellow_l -= 20

        how_much_short = 600 - sum(np.count_nonzero(mask[i, ::]) > 0 for i in range(0, 600))
        if how_much_short > 100 and self.reliability_yellow_line >= 5:
            self.reliability_yellow_line -= 5
        elif how_much_short <= 100 and self.reliability_yellow_line <= 99:
            self.reliability_yellow_line += 5

        msg = UInt8()
        msg.data = self.reliability_yellow_line
        self.pub_yellow_line_reliability.publish(msg)

        if self.is_calibration_mode:
            if self.pub_image_type == "compressed":
                self.pub_image_yellow_lane.publish(self.cvBridge.cv2_to_compressed_imgmsg(mask, "jpg"))
            else:
                self.pub_image_yellow_lane.publish(self.cvBridge.cv2_to_imgmsg(mask, "bgr8"))

        return fraction_num, mask

    def fit_from_lines(self, lane_fit, image):
        nonzero = image.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        margin = 100
        lane_inds = (
            (nonzerox > (lane_fit[0] * (nonzeroy ** 2) + lane_fit[1] * nonzeroy + lane_fit[2] - margin))
            & (nonzerox < (lane_fit[0] * (nonzeroy ** 2) + lane_fit[1] * nonzeroy + lane_fit[2] + margin))
        )
        x = nonzerox[lane_inds]
        y = nonzeroy[lane_inds]
        lane_fit = np.polyfit(y, x, 2)
        ploty = np.linspace(0, image.shape[0] - 1, image.shape[0])
        lane_fitx = lane_fit[0] * ploty ** 2 + lane_fit[1] * ploty + lane_fit[2]
        return lane_fitx, lane_fit

    def sliding_windown(self, img_w, left_or_right):
        histogram = np.sum(img_w[int(img_w.shape[0] / 2) :, :], axis=0)
        midpoint = int(histogram.shape[0] / 2)

        if left_or_right == "left":
            lane_base = np.argmax(histogram[:midpoint])
        else:
            lane_base = np.argmax(histogram[midpoint:]) + midpoint

        nwindows = 20
        window_height = int(img_w.shape[0] / nwindows)
        nonzero = img_w.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        x_current = lane_base
        margin = 50
        minpix = 50
        lane_inds = []

        for window in range(nwindows):
            win_y_low = img_w.shape[0] - (window + 1) * window_height
            win_y_high = img_w.shape[0] - window * window_height
            win_x_low = x_current - margin
            win_x_high = x_current + margin
            good_lane_inds = (
                (nonzeroy >= win_y_low)
                & (nonzeroy < win_y_high)
                & (nonzerox >= win_x_low)
                & (nonzerox < win_x_high)
            ).nonzero()[0]
            lane_inds.append(good_lane_inds)
            if len(good_lane_inds) > minpix:
                x_current = int(np.mean(nonzerox[good_lane_inds]))

        lane_inds = np.concatenate(lane_inds)
        x = nonzerox[lane_inds]
        y = nonzeroy[lane_inds]

        try:
            lane_fit = np.polyfit(y, x, 2)
            self.lane_fit_bef = lane_fit
        except Exception:
            lane_fit = self.lane_fit_bef

        ploty = np.linspace(0, img_w.shape[0] - 1, img_w.shape[0])
        lane_fitx = lane_fit[0] * ploty ** 2 + lane_fit[1] * ploty + lane_fit[2]
        return lane_fitx, lane_fit

    def make_lane(self, cv_image, white_fraction, yellow_fraction):
        warp_zero = np.zeros((cv_image.shape[0], cv_image.shape[1], 1), dtype=np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        color_warp_lines = np.dstack((warp_zero, warp_zero, warp_zero))
        ploty = np.linspace(0, cv_image.shape[0] - 1, cv_image.shape[0])

        if yellow_fraction > 3000:
            pts_left = np.array([np.flipud(np.transpose(np.vstack([self.left_fitx, ploty])))])
            cv2.polylines(color_warp_lines, np.int_([pts_left]), isClosed=False, color=(0, 0, 255), thickness=25)

        if white_fraction > 3000:
            pts_right = np.array([np.transpose(np.vstack([self.right_fitx, ploty]))])
            cv2.polylines(color_warp_lines, np.int_([pts_right]), isClosed=False, color=(255, 255, 0), thickness=25)

        self.is_center_x_exist = True

        if self.reliability_white_line > 50 and self.reliability_yellow_line > 50:
            if white_fraction > 3000 and yellow_fraction > 3000:
                centerx = np.mean([self.left_fitx, self.right_fitx], axis=0)
                pts = np.hstack((pts_left, pts_right))
                pts_center = np.array([np.transpose(np.vstack([centerx, ploty]))])
                cv2.polylines(color_warp_lines, np.int_([pts_center]), isClosed=False, color=(0, 255, 255), thickness=12)
                cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))
            elif white_fraction > 3000:
                centerx = np.subtract(self.right_fitx, 320)
                pts_center = np.array([np.transpose(np.vstack([centerx, ploty]))])
                cv2.polylines(color_warp_lines, np.int_([pts_center]), isClosed=False, color=(0, 255, 255), thickness=12)
            elif yellow_fraction > 3000:
                centerx = np.add(self.left_fitx, 320)
                pts_center = np.array([np.transpose(np.vstack([centerx, ploty]))])
                cv2.polylines(color_warp_lines, np.int_([pts_center]), isClosed=False, color=(0, 255, 255), thickness=12)
        elif self.reliability_yellow_line > 50:
            centerx = np.add(self.left_fitx, 320)
            pts_center = np.array([np.transpose(np.vstack([centerx, ploty]))])
            cv2.polylines(color_warp_lines, np.int_([pts_center]), isClosed=False, color=(0, 255, 255), thickness=12)
        elif self.reliability_white_line > 50:
            centerx = np.subtract(self.right_fitx, 320)
            pts_center = np.array([np.transpose(np.vstack([centerx, ploty]))])
            cv2.polylines(color_warp_lines, np.int_([pts_center]), isClosed=False, color=(0, 255, 255), thickness=12)
        else:
            self.is_center_x_exist = False

        final = cv2.addWeighted(cv_image, 1, color_warp, 0.2, 0)
        final = cv2.addWeighted(final, 1, color_warp_lines, 1, 0)

        if self.is_center_x_exist:
            msg_desired_center = Float64()
            msg_desired_center.data = centerx.item(350)
            self.pub_lane.publish(msg_desired_center)

        if self.pub_image_type == "compressed":
            self.pub_image_lane.publish(self.cvBridge.cv2_to_compressed_imgmsg(final, "jpg"))
        else:
            self.pub_image_lane.publish(self.cvBridge.cv2_to_imgmsg(final, "bgr8"))

    def main(self):
        rospy.spin()


if __name__ == "__main__":
    rospy.init_node("detect_lane")
    node = DetectLane()
    node.main()
