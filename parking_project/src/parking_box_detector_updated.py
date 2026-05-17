#!/usr/bin/env python3

import cv2
import numpy as np
import rospy

from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CompressedImage
from std_msgs.msg import Bool, Float32, String
from geometry_msgs.msg import PolygonStamped, Point32


class ConeDetector:
    def __init__(self):
        rospy.init_node("parking_box_detector_updated", anonymous=True)

        self.bridge = CvBridge()

        self.camera_topic = rospy.get_param("~camera_topic", "/oak/rgb/image_raw")
        self.output_prefix = rospy.get_param("~output_prefix", "/parking_box/front")
        self.use_compressed = rospy.get_param("~use_compressed", False)

        self.roi_top = rospy.get_param("~roi_top_fraction", 0.30)
        self.kernel_size = rospy.get_param("~kernel_size", 3)

        self.min_area = rospy.get_param("~min_cone_area", 20)
        self.max_area = rospy.get_param("~max_cone_area", 20000)
        self.min_cones = rospy.get_param("~min_cones", 1)

        self.min_height = rospy.get_param("~min_cone_height_px", 10)
        self.min_width = rospy.get_param("~min_cone_width_px", 4)

        self.min_tall_ratio = rospy.get_param("~min_height_width_ratio", 1.05)
        self.max_wide_ratio = rospy.get_param("~max_width_height_ratio", 1.20)
        self.reject_flat = rospy.get_param("~reject_flat_blobs", True)

        self.need_white_stripe = rospy.get_param("~require_white_cone_stripe", True)
        self.min_white_pixels = rospy.get_param("~min_white_pixels_near_cone", 8)
        self.white_pad = rospy.get_param("~white_padding_px", 8)

        self.reject_low_flat = rospy.get_param("~reject_bottom_flat_markers", True)
        self.low_marker_y = rospy.get_param("~bottom_marker_y_fraction", 0.82)

        self.valid_x_min = rospy.get_param("~valid_x_min_fraction", 0.00)
        self.valid_x_max = rospy.get_param("~valid_x_max_fraction", 1.00)
        self.valid_y_min = rospy.get_param("~valid_y_min_fraction", 0.05)
        self.valid_y_max = rospy.get_param("~valid_y_max_fraction", 0.98)

        self.pick_far_cones = rospy.get_param("~prefer_far_cones", False)
        self.max_cones_to_use = rospy.get_param("~max_selected_cones", 0)

        self.confirm_frames = rospy.get_param("~confirm_frames", 1)
        self.hold_frames = rospy.get_param("~hold_frames", 20)

        self.show_waiting_image = rospy.get_param("~publish_waiting_debug", True)
        self.waiting_width = rospy.get_param("~waiting_debug_width", 640)
        self.waiting_height = rospy.get_param("~waiting_debug_height", 360)

        self.seen_count = 0
        self.missed_count = 0
        self.saved_box = None
        self.saved_center = None
        self.saved_reason = "init"
        self.got_image = False

        if self.use_compressed:
            rospy.Subscriber(self.camera_topic, CompressedImage, self.read_compressed_image, queue_size=1)
        else:
            rospy.Subscriber(self.camera_topic, Image, self.read_image, queue_size=1)

        self.found_pub = rospy.Publisher(self.output_prefix + "/found", Bool, queue_size=1)
        self.error_pub = rospy.Publisher(self.output_prefix + "/center_error", Float32, queue_size=1)
        self.corners_pub = rospy.Publisher(self.output_prefix + "/corners", PolygonStamped, queue_size=1)
        self.type_pub = rospy.Publisher(self.output_prefix + "/target_type", String, queue_size=1)
        self.mask_pub = rospy.Publisher(self.output_prefix + "/mask", Image, queue_size=1)
        self.debug_pub = rospy.Publisher(self.output_prefix + "/debug_image", Image, queue_size=1)

        rospy.Timer(rospy.Duration(0.5), self.show_waiting_debug)

        rospy.loginfo("cone detector started")
        rospy.loginfo("node_name=%s", rospy.get_name())
        rospy.loginfo("camera_topic=%s", self.camera_topic)
        rospy.loginfo("output_prefix=%s", self.output_prefix)
        rospy.loginfo("need_white_stripe=%s", self.need_white_stripe)

    def show_waiting_debug(self, event):
        if not self.show_waiting_image:
            return

        if self.got_image:
            return

        height = int(self.waiting_height)
        width = int(self.waiting_width)
        debug_img = np.zeros((height, width, 3), dtype=np.uint8)

        cv2.putText(debug_img, "WAITING FOR CAMERA IMAGE", (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        cv2.putText(debug_img, "topic: " + self.camera_topic, (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
        cv2.putText(debug_img, "prefix: " + self.output_prefix, (30, 155),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

        debug_msg = self.bridge.cv2_to_imgmsg(debug_img, encoding="bgr8")
        self.debug_pub.publish(debug_msg)

        self.found_pub.publish(Bool(data=False))
        self.error_pub.publish(Float32(data=0.0))
        self.type_pub.publish(String(data="waiting_for_camera_image"))

        rospy.logwarn_throttle(3.0, "%s waiting for camera image on %s", self.output_prefix, self.camera_topic)

    def make_masks(self, image):
        hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        orange_low = np.array([2, 80, 90], dtype=np.uint8)
        orange_high = np.array([28, 255, 255], dtype=np.uint8)
        orange_mask = cv2.inRange(hsv_img, orange_low, orange_high)

        red_low = np.array([0, 80, 90], dtype=np.uint8)
        red_high = np.array([8, 255, 255], dtype=np.uint8)
        red_mask = cv2.inRange(hsv_img, red_low, red_high)

        cone_mask = cv2.bitwise_or(orange_mask, red_mask)

        white_low = np.array([0, 0, 150], dtype=np.uint8)
        white_high = np.array([180, 80, 255], dtype=np.uint8)
        white_mask = cv2.inRange(hsv_img, white_low, white_high)

        kernel_size = max(1, int(self.kernel_size))
        kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)

        cone_mask = cv2.morphologyEx(cone_mask, cv2.MORPH_OPEN, kernel)
        cone_mask = cv2.morphologyEx(cone_mask, cv2.MORPH_CLOSE, kernel)

        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

        return cone_mask, white_mask

    def point_is_valid(self, x, y, width, height):
        return (
            x >= width * self.valid_x_min and
            x <= width * self.valid_x_max and
            y >= height * self.valid_y_min and
            y <= height * self.valid_y_max
        )

    def check_white_stripe(self, white_mask, x, y, box_width, box_height):
        height, width = white_mask.shape[:2]

        pad = int(self.white_pad)
        x_start = max(0, x - pad)
        y_start = max(0, y - pad)
        x_end = min(width, x + box_width + pad)
        y_end = min(height, y + box_height + pad)

        crop = white_mask[y_start:y_end, x_start:x_end]
        white_count = int(np.count_nonzero(crop))

        return white_count >= int(self.min_white_pixels), white_count

    def find_cone_boxes(self, cone_mask, white_mask):
        height, width = cone_mask.shape[:2]

        num_labels, labels, stats, centers = cv2.connectedComponentsWithStats(cone_mask, connectivity=8)

        cone_boxes = []
        rejected_count = 0

        for label_id in range(1, num_labels):
            x = int(stats[label_id, cv2.CC_STAT_LEFT])
            y = int(stats[label_id, cv2.CC_STAT_TOP])
            box_width = int(stats[label_id, cv2.CC_STAT_WIDTH])
            box_height = int(stats[label_id, cv2.CC_STAT_HEIGHT])
            area = int(stats[label_id, cv2.CC_STAT_AREA])
            center_x, center_y = centers[label_id]

            if area < self.min_area or area > self.max_area:
                rejected_count += 1
                continue

            if box_width < self.min_width or box_height < self.min_height:
                rejected_count += 1
                continue

            if not self.point_is_valid(center_x, center_y, width, height):
                rejected_count += 1
                continue

            tall_ratio = float(box_height) / max(float(box_width), 1.0)
            wide_ratio = float(box_width) / max(float(box_height), 1.0)

            if self.reject_flat:
                if tall_ratio < self.min_tall_ratio:
                    rejected_count += 1
                    continue

                if wide_ratio > self.max_wide_ratio:
                    rejected_count += 1
                    continue

            if self.reject_low_flat:
                is_low = (y + box_height) > height * self.low_marker_y
                is_flat = tall_ratio < 1.20
                if is_low and is_flat:
                    rejected_count += 1
                    continue

            if self.need_white_stripe:
                has_white, white_count = self.check_white_stripe(white_mask, x, y, box_width, box_height)
                if not has_white:
                    rejected_count += 1
                    continue

            cone_boxes.append((x, y, box_width, box_height, area))

        if self.pick_far_cones and len(cone_boxes) > 0:
            cone_boxes = sorted(cone_boxes, key=lambda b: (b[1] + 0.5 * b[3], b[4]))

            if self.max_cones_to_use > 0:
                cone_boxes = cone_boxes[:int(self.max_cones_to_use)]

        return cone_boxes, rejected_count

    def make_target_box(self, cone_boxes, roi_start_y):
        if len(cone_boxes) < self.min_cones:
            return False, None, None, "too_few_cones"

        x_values = []
        y_values = []

        for x, y, box_width, box_height, area in cone_boxes:
            x_values.extend([x, x + box_width])
            y_values.extend([y, y + box_height])

        x_min = float(min(x_values))
        x_max = float(max(x_values))
        y_min = float(min(y_values) + roi_start_y)
        y_max = float(max(y_values) + roi_start_y)

        target_box = np.array([
            [x_min, y_min],
            [x_max, y_min],
            [x_max, y_max],
            [x_min, y_max],
        ], dtype=np.float32)

        target_center = np.array([
            0.5 * (x_min + x_max),
            0.5 * (y_min + y_max),
        ], dtype=np.float32)

        if self.pick_far_cones:
            reason = "accepted_far_cones_%d" % len(cone_boxes)
        else:
            reason = "accepted_cones_%d" % len(cone_boxes)

        return True, target_box, target_center, reason

    def smooth_result(self, found_now, box, center, reason):
        if found_now:
            self.seen_count += 1
            self.missed_count = 0
            self.saved_box = box
            self.saved_center = center
            self.saved_reason = reason

            if self.seen_count >= self.confirm_frames:
                return True, box, center, reason

            return False, None, None, "waiting_for_confirmation"

        self.seen_count = 0
        self.missed_count += 1

        if self.saved_box is not None and self.missed_count <= self.hold_frames:
            return True, self.saved_box, self.saved_center, "holding_last_" + self.saved_reason

        self.saved_box = None
        self.saved_center = None
        self.saved_reason = reason

        return False, None, None, reason

    def publish_box_corners(self, box, header):
        corners_msg = PolygonStamped()
        corners_msg.header = header

        for x, y in box:
            point = Point32()
            point.x = float(x)
            point.y = float(y)
            point.z = 0.0
            corners_msg.polygon.points.append(point)

        self.corners_pub.publish(corners_msg)

    def draw_debug_image(self, frame, roi_start_y, cone_boxes, found, box, center, reason):
        debug_img = frame.copy()
        height, width = debug_img.shape[:2]

        cv2.line(debug_img, (0, roi_start_y), (width - 1, roi_start_y), (255, 0, 0), 2)
        cv2.line(debug_img, (width // 2, 0), (width // 2, height - 1), (0, 255, 255), 2)

        for x, y, box_width, box_height, area in cone_boxes:
            cv2.rectangle(
                debug_img,
                (int(x), int(y + roi_start_y)),
                (int(x + box_width), int(y + box_height + roi_start_y)),
                (255, 255, 0),
                2
            )

        if found:
            cv2.polylines(debug_img, [box.astype(np.int32)], True, (0, 255, 0), 3)
            cv2.circle(debug_img, (int(center[0]), int(center[1])), 6, (0, 0, 255), -1)
            title = "CONE TARGET FOUND"
            title_color = (0, 255, 0)
        else:
            title = "cone target NOT found"
            title_color = (0, 0, 255)

        cv2.putText(debug_img, title, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, title_color, 2)
        cv2.putText(debug_img, reason, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 255, 255), 2)
        cv2.putText(debug_img, "topic: " + self.camera_topic, (20, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        return debug_img

    def read_compressed_image(self, msg):
        image_data = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        if frame is None:
            rospy.logwarn_throttle(2.0, "%s could not decode compressed image", self.output_prefix)
            return

        self.handle_frame(frame, msg.header)

    def read_image(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        self.handle_frame(frame, msg.header)

    def handle_frame(self, frame, header):
        self.got_image = True

        height, width = frame.shape[:2]

        roi_start_y = int(height * self.roi_top)
        roi = frame[roi_start_y:height, :]

        cone_mask, white_mask = self.make_masks(roi)
        cone_boxes, rejected_count = self.find_cone_boxes(cone_mask, white_mask)

        found_now, raw_box, raw_center, raw_reason = self.make_target_box(cone_boxes, roi_start_y)
        found, box, center, reason = self.smooth_result(found_now, raw_box, raw_center, raw_reason)

        if found:
            center_error = float(center[0] - (width / 2.0))
            self.publish_box_corners(box, header)
        else:
            center_error = 0.0

        self.found_pub.publish(Bool(data=found))
        self.error_pub.publish(Float32(data=center_error))
        self.type_pub.publish(String(data=reason))

        mask_msg = self.bridge.cv2_to_imgmsg(cone_mask, encoding="mono8")
        mask_msg.header = header
        self.mask_pub.publish(mask_msg)

        debug_img = self.draw_debug_image(frame, roi_start_y, cone_boxes, found, box, center, reason)
        debug_msg = self.bridge.cv2_to_imgmsg(debug_img, encoding="bgr8")
        debug_msg.header = header
        self.debug_pub.publish(debug_msg)

        rospy.loginfo_throttle(
            1.0,
            "%s found=%s reason=%s cones=%d rejected=%d center_error=%.1f need_white=%s",
            self.output_prefix,
            found,
            reason,
            len(cone_boxes),
            rejected_count,
            center_error,
            self.need_white_stripe
        )

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    node = ConeDetector()
    node.run()
