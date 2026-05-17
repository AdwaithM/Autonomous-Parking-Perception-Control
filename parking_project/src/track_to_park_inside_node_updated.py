#!/usr/bin/env python3

import cv2
import numpy as np
import rospy

from std_msgs.msg import Bool, Float32, String
from geometry_msgs.msg import PolygonStamped
from ackermann_msgs.msg import AckermannDrive


class ConeCameraState:
    def __init__(self, prefix):
        self.prefix = prefix
        self.found = False
        self.error = 0.0
        self.area = 0.0
        self.center_y = 0.0
        self.have_corners = False
        self.target_type = "none"

        rospy.Subscriber(prefix + "/found", Bool, self.found_callback, queue_size=1)
        rospy.Subscriber(prefix + "/center_error", Float32, self.error_callback, queue_size=1)
        rospy.Subscriber(prefix + "/corners", PolygonStamped, self.corners_callback, queue_size=1)
        rospy.Subscriber(prefix + "/target_type", String, self.type_callback, queue_size=1)

    def found_callback(self, msg):
        self.found = msg.data

    def error_callback(self, msg):
        self.error = msg.data

    def type_callback(self, msg):
        self.target_type = msg.data

    def corners_callback(self, msg):
        if len(msg.polygon.points) < 4:
            self.area = 0.0
            self.center_y = 0.0
            self.have_corners = False
            return

        points = []
        for p in msg.polygon.points:
            points.append([p.x, p.y])

        points = np.array(points, dtype=np.float32)
        self.area = float(abs(cv2.contourArea(points)))
        self.center_y = float(np.mean(points[:, 1]))
        self.have_corners = True

    def ready(self, min_area, min_y):
        return (
            self.found
            and self.have_corners
            and self.area >= min_area
            and self.center_y >= min_y
        )


class TrackToParkInsideNodeUpdated:
    def __init__(self):
        rospy.init_node("track_to_park_inside_node_updated")

        self.cmd_topic = rospy.get_param("~cmd_topic", "/ackermann_cmd")

        self.front_prefix = rospy.get_param("~front_prefix", "/parking_box/front")
        self.fl_prefix = rospy.get_param("~fl_prefix", "/parking_box/fl")
        self.fr_prefix = rospy.get_param("~fr_prefix", "/parking_box/fr")
        self.bl_prefix = rospy.get_param("~bl_prefix", "/parking_box/bl")
        self.br_prefix = rospy.get_param("~br_prefix", "/parking_box/br")

        self.front = ConeCameraState(self.front_prefix)
        self.fl = ConeCameraState(self.fl_prefix)
        self.fr = ConeCameraState(self.fr_prefix)
        self.bl = ConeCameraState(self.bl_prefix)
        self.br = ConeCameraState(self.br_prefix)

        self.forward_speed = rospy.get_param("~forward_speed", 0.18)
        self.approach_speed = rospy.get_param("~approach_speed", 0.16)
        self.turn_speed = rospy.get_param("~turn_speed", 0.12)
        self.enter_speed = rospy.get_param("~enter_speed", 0.14)
        self.straighten_speed = rospy.get_param("~straighten_speed", 0.09)

        self.right_turn_steer = rospy.get_param("~right_turn_steer", -1.25)
        self.left_straighten_steer = rospy.get_param("~left_straighten_steer", 0.50)

        self.front_min_area = rospy.get_param("~front_min_area", 20.0)
        self.front_min_y = rospy.get_param("~front_min_y", 60.0)
        self.front_close_area = rospy.get_param("~front_close_area", 5000.0)
        self.front_close_y = rospy.get_param("~front_close_y", 470.0)

        self.fl_turn_confirm_frames = rospy.get_param("~fl_turn_confirm_frames", 9)
        self.fl_turn_seen_count = 0

        self.fl_turn_strict_area = rospy.get_param("~fl_turn_strict_area", 1200.0)
        self.fl_turn_strict_y = rospy.get_param("~fl_turn_strict_y", 130.0)
        self.use_strict_fl_turn = rospy.get_param("~use_strict_fl_turn", True)

        self.fr_emergency_area = rospy.get_param("~fr_emergency_area", 25000.0)
        self.fr_emergency_y = rospy.get_param("~fr_emergency_y", 430.0)

        self.bl_straighten_area = rospy.get_param("~bl_straighten_area", 80.0)
        self.bl_straighten_y = rospy.get_param("~bl_straighten_y", 0.0)
        self.bl_confirm_frames = rospy.get_param("~bl_confirm_frames", 1)
        self.bl_seen_count = 0

        self.rear_min_area = rospy.get_param("~rear_min_area", 250.0)
        self.rear_min_y = rospy.get_param("~rear_min_y", 40.0)
        self.rear_confirm_frames = rospy.get_param("~rear_confirm_frames", 2)
        self.rear_seen_count = 0

        self.mode = "FORWARD"

        self.cmd_pub = rospy.Publisher(self.cmd_topic, AckermannDrive, queue_size=1)
        self.status_pub = rospy.Publisher("/track_to_park/status", String, queue_size=1)

        rospy.loginfo("Cone parking controller started")
        rospy.loginfo("Sequence:")
        rospy.loginfo("1) TURN_RIGHT hard")
        rospy.loginfo("2) FL confirms for 9 frames -> ENTER_STRAIGHT")
        rospy.loginfo("3) Go straight into cones")
        rospy.loginfo("4) ONLY BL sees cone -> STRAIGHTEN_LEFT")
        rospy.loginfo("5) BL and BR see cones -> STOP")

    def publish_cmd(self, speed, steer):
        cmd = AckermannDrive()
        cmd.speed = float(speed)
        cmd.steering_angle = float(steer)
        self.cmd_pub.publish(cmd)

    def change_mode(self, new_mode):
        if self.mode != new_mode:
            rospy.loginfo("Switching mode: %s -> %s", self.mode, new_mode)
            self.mode = new_mode

            if new_mode == "TURN_RIGHT":
                self.fl_turn_seen_count = 0

            if new_mode == "ENTER_STRAIGHT":
                self.bl_seen_count = 0
                self.rear_seen_count = 0

            if new_mode == "STRAIGHTEN_LEFT":
                self.rear_seen_count = 0

    def front_ready(self):
        return self.front.ready(self.front_min_area, self.front_min_y)

    def front_close(self):
        return self.front.ready(self.front_close_area, self.front_close_y)

    def fl_ready_to_end_turn_now(self):
        if self.use_strict_fl_turn:
            return self.fl.ready(self.fl_turn_strict_area, self.fl_turn_strict_y)

        return self.fl.ready(250.0, 60.0)

    def turn_right_done(self):
        if self.fl_ready_to_end_turn_now():
            self.fl_turn_seen_count += 1
        else:
            self.fl_turn_seen_count = 0

        fl_confirmed = self.fl_turn_seen_count >= self.fl_turn_confirm_frames
        fr_emergency = self.fr.ready(self.fr_emergency_area, self.fr_emergency_y)

        return fl_confirmed or fr_emergency

    def back_left_confirmed(self):
        if self.bl.ready(self.bl_straighten_area, self.bl_straighten_y):
            self.bl_seen_count += 1
        else:
            self.bl_seen_count = 0

        return self.bl_seen_count >= self.bl_confirm_frames

    def both_rear_see_cones_now(self):
        bl_ok = self.bl.ready(self.rear_min_area, self.rear_min_y)
        br_ok = self.br.ready(self.rear_min_area, self.rear_min_y)
        return bl_ok and br_ok

    def both_rear_confirmed(self):
        if self.both_rear_see_cones_now():
            self.rear_seen_count += 1
        else:
            self.rear_seen_count = 0

        return self.rear_seen_count >= self.rear_confirm_frames

    def publish_status(self, speed, steer):
        status = (
            "mode=%s fl_turn_count=%d/%d bl_count=%d/%d rear_count=%d/%d "
            "front=(%s a=%.0f y=%.0f e=%.0f) "
            "fl=(%s a=%.0f y=%.0f) fr=(%s a=%.0f y=%.0f) "
            "bl=(%s a=%.0f y=%.0f) br=(%s a=%.0f y=%.0f) "
            "speed=%.2f steer=%.3f"
            % (
                self.mode,
                self.fl_turn_seen_count,
                self.fl_turn_confirm_frames,
                self.bl_seen_count,
                self.bl_confirm_frames,
                self.rear_seen_count,
                self.rear_confirm_frames,
                self.front.found, self.front.area, self.front.center_y, self.front.error,
                self.fl.found, self.fl.area, self.fl.center_y,
                self.fr.found, self.fr.area, self.fr.center_y,
                self.bl.found, self.bl.area, self.bl.center_y,
                self.br.found, self.br.area, self.br.center_y,
                speed,
                steer,
            )
        )

        self.status_pub.publish(status)
        rospy.loginfo_throttle(1.0, status)

    def run(self):
        rate = rospy.Rate(20)

        while not rospy.is_shutdown():
            speed = 0.0
            steer = 0.0

            if self.mode == "FORWARD":
                if self.front_ready():
                    self.change_mode("APPROACH_CONES")
                else:
                    speed = self.forward_speed
                    steer = 0.0
                    self.publish_cmd(speed, steer)
                    self.publish_status(speed, steer)
                    rate.sleep()
                    continue

            if self.mode == "APPROACH_CONES":
                speed = self.approach_speed
                steer = 0.0

                if self.front_close():
                    self.change_mode("TURN_RIGHT")

                self.publish_cmd(speed, steer)

            elif self.mode == "TURN_RIGHT":
                speed = self.turn_speed
                steer = self.right_turn_steer

                if self.turn_right_done():
                    self.change_mode("ENTER_STRAIGHT")

                self.publish_cmd(speed, steer)

            elif self.mode == "ENTER_STRAIGHT":
                speed = self.enter_speed
                steer = 0.0

                if self.back_left_confirmed():
                    self.change_mode("STRAIGHTEN_LEFT")

                self.publish_cmd(speed, steer)

            elif self.mode == "STRAIGHTEN_LEFT":
                speed = self.straighten_speed
                steer = self.left_straighten_steer

                if self.both_rear_confirmed():
                    self.change_mode("STOP")

                self.publish_cmd(speed, steer)

            elif self.mode == "STOP":
                speed = 0.0
                steer = 0.0
                self.publish_cmd(0.0, 0.0)

            self.publish_status(speed, steer)
            rate.sleep()


if __name__ == "__main__":
    node = TrackToParkInsideNodeUpdated()
    node.run()
