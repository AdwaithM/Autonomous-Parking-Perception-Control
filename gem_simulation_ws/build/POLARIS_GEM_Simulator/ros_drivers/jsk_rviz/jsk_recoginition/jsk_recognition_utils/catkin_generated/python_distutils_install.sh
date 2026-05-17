#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/adwaith/host/gem_simulation_ws/src/POLARIS_GEM_Simulator/ros_drivers/jsk_rviz/jsk_recoginition/jsk_recognition_utils"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/adwaith/host/gem_simulation_ws/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/adwaith/host/gem_simulation_ws/install/lib/python3/dist-packages:/home/adwaith/host/gem_simulation_ws/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/adwaith/host/gem_simulation_ws/build" \
    "/usr/bin/python3" \
    "/home/adwaith/host/gem_simulation_ws/src/POLARIS_GEM_Simulator/ros_drivers/jsk_rviz/jsk_recoginition/jsk_recognition_utils/setup.py" \
    egg_info --egg-base /home/adwaith/host/gem_simulation_ws/build/POLARIS_GEM_Simulator/ros_drivers/jsk_rviz/jsk_recoginition/jsk_recognition_utils \
    build --build-base "/home/adwaith/host/gem_simulation_ws/build/POLARIS_GEM_Simulator/ros_drivers/jsk_rviz/jsk_recoginition/jsk_recognition_utils" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/adwaith/host/gem_simulation_ws/install" --install-scripts="/home/adwaith/host/gem_simulation_ws/install/bin"
