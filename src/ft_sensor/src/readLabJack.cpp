// Copyright 2022 Sizhe Tian, Soft Robotic Lab, ETH

#include "U3/u3Streamer.h"
#include "ros/ros.h"
#include "ros/console.h"
#include "std_msgs/Float32MultiArray.h"

int main(int argc, char **argv) {
  ros::init(argc, argv, "u3_streamming");

  ros::NodeHandle n;

  ros::Publisher u3_pub = n.advertise<std_msgs::Float32MultiArray >("/force_torque_sensor_raw/u3", 1000);

  u3Streamer u3;

  if (!u3.isInit()) {
    ROS_ERROR("U3 initialzation unsuccessful");
    return -1;
  }

  ROS_INFO("read Lab Jack started");

  // Read labjack output data without delay
  // limit the speed in getStreamData() function with numReadsPerDisplay
  while (ros::ok()) {
    std::array<double, NumChannels> voltages;
    u3.getStreamData(voltages);
    std_msgs::Float32MultiArray msg;
    msg.layout.dim.push_back(std_msgs::MultiArrayDimension());
    msg.layout.dim[0].size = 4;
    msg.layout.dim[0].stride = 1;
    msg.layout.dim[0].label = "voltages_u3";

    msg.data.clear();
    msg.data.assign(voltages.data(), voltages.data() + NumChannels);
    u3_pub.publish(msg);
    ros::spinOnce();
  }

  return 0;
}
