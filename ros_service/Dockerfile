FROM ros:kilted
WORKDIR /ws
COPY ros_zenoh_msgs src/ros_zenoh_msgs
RUN . /opt/ros/kilted/setup.sh && colcon build
COPY main.py .
ENTRYPOINT ["bash", "-c", "source install/setup.bash && exec python3 main.py \"$@\"", "main.py"]
