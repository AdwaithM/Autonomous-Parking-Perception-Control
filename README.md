# Autonomous Parking Perception and Control

This project is my autonomous parking demo using the Polaris GEM e4 simulator. The car drives through the highbay scene, stops at a stop sign, waits, and then parks inside a cone-marked parking spot.
Youtube Link: https://youtu.be/s4hsUfMD6Ms

The system is split into three main parts:

- `parking_box_detector_updated.py` detects the parking cones from the camera images.
- `track_to_park_inside_node_updated.py` controls the parking maneuver using a simple state machine.
- `yolo_safety_behavior_node.py` checks YOLO stop sign detections and stops the car before letting it continue.

The parking controller publishes to `/parking_cmd_raw`, and the safety node publishes the final command to `/ackermann_cmd`. This lets the stop sign logic override the car when needed.

## Scripts used

Parking project scripts:

```text
~/host/parking_project/src/parking_box_detector_updated.py
~/host/parking_project/src/track_to_park_inside_node_updated.py
~/host/parking_project/src/yolo_safety_behavior_node.py
```

YOLO detector script:

```text
~/host/gem_simulation_ws/src/POLARIS_GEM_Simulator/gem_simulator/gem_gazebo/scripts/yolo_detector.py
```

## How to run

Run each command in a separate terminal.

### Terminal 1: start the simulator

```bash
cd ~/host/gem_simulation_ws

roslaunch gem_launch gem_init.launch world_name:="highbay_track.world" x:=15.307 y:=-22.197 yaw:=3.1416 custom_scene:=true
```

### Terminal 2: front cone detector

```bash
cd ~/host/parking_project/src

python3 parking_box_detector_updated.py __name:=parking_box_detector_front _camera_topic:=/oak/rgb/image_raw _output_prefix:=/parking_box/front _roi_top_fraction:=0.30 _kernel_size:=3 _min_cone_area:=20 _max_cone_area:=20000 _min_cones:=2 _min_cone_height_px:=8 _min_cone_width_px:=4 _min_height_width_ratio:=0.75 _max_width_height_ratio:=1.80 _reject_flat_blobs:=true _prefer_far_cones:=false _valid_x_min_fraction:=0.00 _valid_x_max_fraction:=1.00 _valid_y_min_fraction:=0.05 _valid_y_max_fraction:=0.95 _confirm_frames:=1 _hold_frames:=20
```

### Terminal 3: front-right cone detector

```bash
cd ~/host/parking_project/src

python3 parking_box_detector_updated.py __name:=parking_box_detector_fr _camera_topic:=/camera_fr/arena_camera_node/image_raw _output_prefix:=/parking_box/fr _roi_top_fraction:=0.10 _kernel_size:=3 _min_cone_area:=20 _max_cone_area:=20000 _min_cones:=1 _min_cone_height_px:=8 _min_cone_width_px:=4 _min_height_width_ratio:=0.75 _max_width_height_ratio:=1.80 _reject_flat_blobs:=true _prefer_far_cones:=true _max_selected_cones:=1 _valid_x_min_fraction:=0.00 _valid_x_max_fraction:=1.00 _valid_y_min_fraction:=0.05 _valid_y_max_fraction:=0.85 _confirm_frames:=1 _hold_frames:=20
```

### Terminal 4: front-left cone detector

```bash
cd ~/host/parking_project/src

python3 parking_box_detector_updated.py __name:=parking_box_detector_fl _camera_topic:=/camera_fl/arena_camera_node/image_raw _output_prefix:=/parking_box/fl _roi_top_fraction:=0.10 _kernel_size:=3 _min_cone_area:=20 _max_cone_area:=20000 _min_cones:=1 _min_cone_height_px:=8 _min_cone_width_px:=4 _min_height_width_ratio:=0.75 _max_width_height_ratio:=1.80 _reject_flat_blobs:=true _prefer_far_cones:=true _max_selected_cones:=1 _valid_x_min_fraction:=0.00 _valid_x_max_fraction:=1.00 _valid_y_min_fraction:=0.05 _valid_y_max_fraction:=0.85 _confirm_frames:=1 _hold_frames:=20
```

### Terminal 5: back-left cone detector

```bash
cd ~/host/parking_project/src

python3 parking_box_detector_updated.py __name:=parking_box_detector_bl _camera_topic:=/camera_rl/arena_camera_node/image_raw _output_prefix:=/parking_box/bl _roi_top_fraction:=0.10 _kernel_size:=3 _min_cone_area:=20 _max_cone_area:=20000 _min_cones:=1 _min_cone_height_px:=12 _min_cone_width_px:=4 _min_height_width_ratio:=1.15 _max_width_height_ratio:=1.05 _reject_flat_blobs:=true _require_white_cone_stripe:=true _min_white_pixels_near_cone:=8 _white_padding_px:=8 _reject_bottom_flat_markers:=true _bottom_marker_y_fraction:=0.82 _prefer_far_cones:=false _confirm_frames:=1 _hold_frames:=10
```

### Terminal 6: back-right cone detector

```bash
cd ~/host/parking_project/src

python3 parking_box_detector_updated.py __name:=parking_box_detector_br _camera_topic:=/camera_rr/arena_camera_node/image_raw _output_prefix:=/parking_box/br _roi_top_fraction:=0.10 _kernel_size:=3 _min_cone_area:=20 _max_cone_area:=20000 _min_cones:=1 _min_cone_height_px:=12 _min_cone_width_px:=4 _min_height_width_ratio:=1.15 _max_width_height_ratio:=1.05 _reject_flat_blobs:=true _require_white_cone_stripe:=true _min_white_pixels_near_cone:=8 _white_padding_px:=8 _reject_bottom_flat_markers:=true _bottom_marker_y_fraction:=0.82 _prefer_far_cones:=false _confirm_frames:=1 _hold_frames:=10
```

### Terminal 7: YOLO stop sign detector

```bash
cd ~/host/gem_simulation_ws/src/POLARIS_GEM_Simulator/gem_simulator/gem_gazebo/scripts

python3 yolo_detector.py _image_topic:=/oak/rgb/image_raw _model:=yolov8n.pt _confidence:=0.4 _img_size:=320 _device:=cpu _detections_topic:=/yolo/detections _annotated_topic:=/yolo/image_annotated _info_topic:=/yolo/detection_info
```

### Terminal 8: parking controller

```bash
cd ~/host/parking_project/src

python3 track_to_park_inside_node_updated.py _cmd_topic:=/parking_cmd_raw _front_prefix:=/parking_box/front _fl_prefix:=/parking_box/fl _fr_prefix:=/parking_box/fr _bl_prefix:=/parking_box/bl _br_prefix:=/parking_box/br _forward_speed:=0.18 _approach_speed:=0.16 _turn_speed:=0.12 _enter_speed:=0.14 _straighten_speed:=0.09 _right_turn_steer:=-1.25 _left_straighten_steer:=0.50 _front_min_area:=20 _front_min_y:=60 _front_close_area:=5000 _front_close_y:=470 _use_strict_fl_turn:=true _fl_turn_strict_area:=1200 _fl_turn_strict_y:=130 _fl_turn_confirm_frames:=14 _fr_emergency_area:=25000 _fr_emergency_y:=430 _bl_straighten_area:=80 _bl_straighten_y:=0 _bl_confirm_frames:=1 _rear_min_area:=250 _rear_min_y:=40 _rear_confirm_frames:=2
```

### Terminal 9: stop sign safety node

```bash
cd ~/host/parking_project/src

python3 yolo_safety_behavior_node.py _input_cmd_topic:=/parking_cmd_raw _output_cmd_topic:=/ackermann_cmd _yolo_topic:=/yolo/detections _detection_timeout:=2.0 _use_stop_sign:=true _stop_sign_area_fraction:=0.006 _stop_sign_bottom_y_fraction:=0.65 _stop_sign_center_deadband_fraction:=0.65 _stop_sign_wait_seconds:=20.0 _stop_sign_cooldown_frames:=500
```

## What should happen

The car should drive forward, stop near the stop sign for 20 seconds, continue toward the cones, turn into the cone box, straighten, and stop inside the parking area.

Useful debug topics:

```bash
rostopic echo /track_to_park/status
rostopic echo /parking_cmd_raw
rostopic echo /ackermann_cmd
rqt_image_view /yolo/image_annotated
```
