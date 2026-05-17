execute_process(COMMAND "/home/adwaith/host/gem_simulation_ws/build/POLARIS_GEM_Simulator/ros_drivers/jsk_rviz/jsk_topic_tools/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/adwaith/host/gem_simulation_ws/build/POLARIS_GEM_Simulator/ros_drivers/jsk_rviz/jsk_topic_tools/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
