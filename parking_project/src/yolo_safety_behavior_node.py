#!/usr/bin/env python3

import threading
import rospy
import rostopic

from ackermann_msgs.msg import AckermannDrive


class StopSignNode:
    def __init__(self):
        rospy.init_node("yolo_safety_behavior_node")

        self.input_topic = rospy.get_param("~input_cmd_topic", "/parking_cmd_raw")
        self.output_topic = rospy.get_param("~output_cmd_topic", "/ackermann_cmd")
        self.yolo_topic = rospy.get_param("~yolo_topic", "/yolo/detections")
        self.debug = rospy.get_param("~debug", True)

        self.stop_names = set(rospy.get_param("~stop_sign_classes", ["stop sign", "stop_sign"]))

        self.img_width = rospy.get_param("~image_w", 1240.0)
        self.img_height = rospy.get_param("~image_h", 680.0)

        self.use_stop_sign = rospy.get_param("~use_stop_sign", True)
        self.min_stop_area = rospy.get_param("~stop_sign_area_fraction", 0.045)
        self.stop_center_limit = rospy.get_param("~stop_sign_center_deadband_fraction", 0.45)
        self.min_stop_bottom = rospy.get_param("~stop_sign_bottom_y_fraction", 0.65)
        self.stop_wait_time = rospy.get_param("~stop_sign_wait_seconds", 5.0)

        self.cooldown_frames = rospy.get_param("~stop_sign_cooldown_frames", 180)
        self.cooldown_count = 0

        self.is_waiting = False
        self.wait_start_time = None

        self.detection_timeout = rospy.get_param("~detection_timeout", 2.0)

        self.lock = threading.Lock()
        self.last_cmd = AckermannDrive()
        self.has_cmd = False
        self.last_detection_time = None
        self.detections = []

        self.cmd_pub = rospy.Publisher(self.output_topic, AckermannDrive, queue_size=1)

        rospy.Subscriber(self.input_topic, AckermannDrive, self.save_cmd, queue_size=1)
        self.setup_yolo_subscriber()

        rospy.Timer(rospy.Duration(0.05), self.update)

        rospy.loginfo("stop sign safety node started")
        rospy.loginfo("input_topic=%s", self.input_topic)
        rospy.loginfo("output_topic=%s", self.output_topic)
        rospy.loginfo("yolo_topic=%s", self.yolo_topic)

    def setup_yolo_subscriber(self):
        topic_type, _, _ = rostopic.get_topic_type(self.yolo_topic)

        if topic_type is None:
            rospy.logwarn("Could not find YOLO topic type for %s", self.yolo_topic)
            rospy.logwarn("Start YOLO first, then restart this node.")
            return

        rospy.loginfo("YOLO topic type: %s", topic_type)

        if topic_type == "darknet_ros_msgs/BoundingBoxes":
            from darknet_ros_msgs.msg import BoundingBoxes
            rospy.Subscriber(self.yolo_topic, BoundingBoxes, self.read_darknet_boxes, queue_size=1)
            rospy.loginfo("using darknet_ros_msgs/BoundingBoxes")
            return

        if topic_type == "vision_msgs/Detection2DArray":
            from vision_msgs.msg import Detection2DArray
            rospy.Subscriber(self.yolo_topic, Detection2DArray, self.read_vision_boxes, queue_size=1)
            rospy.loginfo("using vision_msgs/Detection2DArray")
            return

        rospy.logerr("Unsupported YOLO topic type: %s", topic_type)

    def save_cmd(self, msg):
        with self.lock:
            self.last_cmd = msg
            self.has_cmd = True

    def read_darknet_boxes(self, msg):
        boxes = []

        for box in msg.bounding_boxes:
            boxes.append({
                "name": str(box.Class).strip().lower(),
                "score": float(box.probability),
                "x1": int(box.xmin),
                "y1": int(box.ymin),
                "x2": int(box.xmax),
                "y2": int(box.ymax),
            })

        with self.lock:
            self.detections = boxes
            self.last_detection_time = rospy.Time.now()

    def read_vision_boxes(self, msg):
        boxes = []

        for item in msg.detections:
            name = "unknown"
            score = 0.0

            if len(item.results) > 0:
                result = item.results[0]

                if hasattr(result, "id"):
                    name = self.name_from_id(result.id)
                elif hasattr(result, "hypothesis") and hasattr(result.hypothesis, "class_id"):
                    name = self.name_from_id(result.hypothesis.class_id)

                if hasattr(result, "score"):
                    score = float(result.score)
                elif hasattr(result, "hypothesis") and hasattr(result.hypothesis, "score"):
                    score = float(result.hypothesis.score)

            center_x = float(item.bbox.center.x)
            center_y = float(item.bbox.center.y)
            size_x = float(item.bbox.size_x)
            size_y = float(item.bbox.size_y)

            boxes.append({
                "name": str(name).strip().lower(),
                "score": score,
                "x1": int(center_x - size_x / 2.0),
                "y1": int(center_y - size_y / 2.0),
                "x2": int(center_x + size_x / 2.0),
                "y2": int(center_y + size_y / 2.0),
            })

        with self.lock:
            self.detections = boxes
            self.last_detection_time = rospy.Time.now()

    def name_from_id(self, class_id):
        coco_names = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
            9: "traffic light",
            11: "stop sign",
        }

        try:
            return coco_names.get(int(class_id), str(class_id))
        except Exception:
            return str(class_id)

    def detections_are_fresh(self):
        if self.last_detection_time is None:
            return False

        age = (rospy.Time.now() - self.last_detection_time).to_sec()
        return age <= self.detection_timeout

    def get_box_numbers(self, box):
        image_area = self.img_width * self.img_height

        x1 = float(box["x1"])
        y1 = float(box["y1"])
        x2 = float(box["x2"])
        y2 = float(box["y2"])

        if x2 < x1:
            x1, x2 = x2, x1

        if y2 < y1:
            y1, y2 = y2, y1

        box_width = max(0.0, x2 - x1)
        box_height = max(0.0, y2 - y1)

        area_ratio = (box_width * box_height) / max(image_area, 1.0)
        box_center_x = 0.5 * (x1 + x2)
        center_error = (box_center_x - self.img_width / 2.0) / self.img_width
        bottom_ratio = y2 / self.img_height

        return area_ratio, center_error, bottom_ratio

    def stop_sign_is_close(self, boxes):
        if not self.use_stop_sign:
            return False

        if self.cooldown_count > 0:
            return False

        for box in boxes:
            if box["name"] not in self.stop_names:
                continue

            area_ratio, center_error, bottom_ratio = self.get_box_numbers(box)

            is_centered = abs(center_error) <= self.stop_center_limit
            is_big_enough = area_ratio >= self.min_stop_area
            is_low_enough = bottom_ratio >= self.min_stop_bottom

            rospy.loginfo_throttle(
                1.0,
                "stop_sign_check area=%.3f/%.3f bottom=%.2f/%.2f centered=%s",
                area_ratio,
                self.min_stop_area,
                bottom_ratio,
                self.min_stop_bottom,
                is_centered,
            )

            if is_centered and is_big_enough and is_low_enough:
                return True

        return False

    def make_drive_cmd(self, speed, steer):
        cmd = AckermannDrive()
        cmd.speed = float(speed)
        cmd.steering_angle = float(steer)
        return cmd

    def start_waiting(self):
        self.is_waiting = True
        self.wait_start_time = rospy.Time.now()
        rospy.loginfo("stop sign found close enough, waiting %.1f seconds", self.stop_wait_time)

    def get_wait_cmd(self):
        if not self.is_waiting:
            return None, "not_waiting"

        waited = (rospy.Time.now() - self.wait_start_time).to_sec()

        if waited >= self.stop_wait_time:
            self.is_waiting = False
            self.wait_start_time = None
            self.cooldown_count = self.cooldown_frames
            rospy.loginfo("done waiting at stop sign")
            return None, "done_waiting"

        return self.make_drive_cmd(0.0, 0.0), "waiting_at_stop_sign_%.1f" % waited

    def update(self, event):
        with self.lock:
            if not self.has_cmd:
                return

            normal_cmd = self.last_cmd

            if self.detections_are_fresh():
                boxes = list(self.detections)
            else:
                boxes = []

        if self.cooldown_count > 0:
            self.cooldown_count -= 1

        wait_cmd, reason = self.get_wait_cmd()
        if wait_cmd is not None:
            self.cmd_pub.publish(wait_cmd)
            self.print_status(reason, normal_cmd, wait_cmd, boxes)
            return

        if self.stop_sign_is_close(boxes):
            self.start_waiting()
            stop_cmd = self.make_drive_cmd(0.0, 0.0)
            self.cmd_pub.publish(stop_cmd)
            self.print_status("start_stop_sign_wait", normal_cmd, stop_cmd, boxes)
            return

        self.cmd_pub.publish(normal_cmd)
        self.print_status("normal_driving", normal_cmd, normal_cmd, boxes)

    def print_status(self, reason, normal_cmd, final_cmd, boxes):
        if not self.debug:
            return

        rospy.loginfo_throttle(
            1.0,
            "stop safety: %s normal=(%.2f, %.3f) final=(%.2f, %.3f) detections=%d cooldown=%d",
            reason,
            normal_cmd.speed,
            normal_cmd.steering_angle,
            final_cmd.speed,
            final_cmd.steering_angle,
            len(boxes),
            self.cooldown_count,
        )

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    node = StopSignNode()
    node.run()
