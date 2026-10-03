# amr_ws: Autonomous Warehouse Mobile Robot (ROS 2 Jazzy)

Differential-drive AMR in a Gazebo Harmonic warehouse, built with SLAM Toolbox,
AMCL, robot_localization, Nav2 and ros2_control.


## Status
- [x] Phase 1: robot model, Gazebo warehouse, sensors, ros2_control, teleop
- [ ] Phase 2: EKF, SLAM mapping, AMCL localization
- [ ] Phase 3: Nav2, obstacle avoidance, missions

## Requirements
Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic

## Build
    git clone git@github.com:Aleesha/amr_ws.git
    cd amr_ws
    rosdep install --from-paths src -y --ignore-src
    colcon build --symlink-install && source install/setup.bash

## Run the simulation
    ros2 launch amr_gazebo sim.launch.py

## Drive
    ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
      -r cmd_vel:=/diff_drive_controller/cmd_vel -p stamped:=true -p use_sim_time:=true
