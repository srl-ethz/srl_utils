// Copyright 2022 Sizhe Tian, Soft Robotic Lab, ETH
// Adatpted from samples in ATI ATIDAQ F/T C Library
/* ATIDAQ F/T C Library
 * v1.0.4
 * Copyright (c) 2001 ATI Industrial Automation
 *
 * The MIT License
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included
 * in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */

/* ftconvert.cpp
 configuring a DAQ F/T system
 save most recent voltage measurement
 performing force/torque calculations
*/

#include "ftconverter.h"
#include <ros/console.h>
#include <ros/package.h>
#include <stdio.h>

FTConverter::FTConverter(char *calfilepath) {
  // create Calibration struct
  cal_ = createCalibration(calfilepath, 1);
  if (cal_ == NULL) {
    ROS_ERROR("\nSpecified calibration could not be loaded.\n");
    return;
  }

  // No tranformation will be applied
  transformation_ = std::array<float, 6>{0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

  // Set force units.
  // This step is optional; by default, the units are inherited from the
  // calibration file.
  sts_ = SetForceUnits(cal_, "N");
  switch (sts_) {
  case 0:
    break;  // successful completion
  case 1:
    ROS_ERROR("Invalid Calibration struct");
    return;
  case 2:
    ROS_ERROR("Invalid force units");
    return;
  default:
    ROS_ERROR("Unknown error");
    return;
  }

  // Set torque units.
  // This step is optional; by default, the units are inherited from the
  // calibration file.
  sts_ = SetTorqueUnits(cal_, "N-m");
  switch (sts_) {
  case 0:
    break;  // successful completion
  case 1:
    ROS_ERROR("Invalid Calibration struct");
    return;
  case 2:
    ROS_ERROR("Invalid torque units");
    return;
  default:
    ROS_ERROR("Unknown error");
    return;
  }

  // Set tool transform.
  // This line is only required if you want to move or rotate the sensor's
  // coordinate system. This example tool transform translates the coordinate
  // system 20 mm along the Z-axis and rotates it 45 degrees about the X-axis.
  sts_ = SetToolTransform(cal_, transformation_.data(), "mm", "degrees");
  switch (sts_) {
  case 0:
    break;  // successful completion
  case 1:
    ROS_ERROR("Invalid Calibration struct");
    return;
  case 2:
    ROS_ERROR("Invalid distance units");
    return;
  case 3:
    ROS_ERROR("Invalid angle units");
    return;
  default:
    ROS_ERROR("Unknown error");
    return;
  }

  ros::NodeHandle nh;
}

FTConverter::~FTConverter() { destroyCalibration(cal_); }

void FTConverter::initBias() {
  voltage_mtx_.lock();
  bias_ = voltages_;
  voltage_mtx_.unlock();
  biasInit_ = true;

  Bias(cal_, bias_.data());

  std::string Bias_init_msg = "Bias is initialized to be : [ ";
  for (auto i : bias_) {
    Bias_init_msg += std::to_string(i);
    Bias_init_msg += ", ";
  }
  Bias_init_msg += " ]";

  std::cout << Bias_init_msg << std::endl;
}

void FTConverter::getMeasurement(std::array<float, 6> &measurement) {
  // only calculate ft measurements after bias is initialized
  if (biasInit_) {
    ConvertToFT(cal_, voltages_.data(), measurement.data());
  } else {
    ROS_WARN("bias not initialized, please initialize bias first");
  }
}

void FTConverter::u3Callback(std_msgs::Float32MultiArray msg) {
  // Check message dimension
  if (msg.layout.dim[0].size != 4) {
    ROS_ERROR("Please check Labjack output");
    return;
  }

  voltage_mtx_.lock();
  for (int i = 0; i < 4; i++) {
    // save reading from labjack (SG2 - SG5)
    voltages_.at(i + 2) = msg.data[i];
  }
  voltage_mtx_.unlock();
}

void FTConverter::adcCallback(std_msgs::Float32MultiArray msg) {
  // Check message dimension
  if (msg.layout.dim[0].size != 2) {
    ROS_ERROR("Please check ADC output");
    return;
  }

  if (msg.data[0] > 6. || msg.data[0] < -6. || msg.data[1] > 6. ||
      msg.data[1] < -6.) {
    ROS_WARN("ADC is saturated, please adjust the measurement range");
    return;
  }

  voltage_mtx_.lock();
  // use adc to read first two channels (SG0, SG1)
  voltages_.at(0) = msg.data[0];
  voltages_.at(1) = msg.data[1];
  voltage_mtx_.unlock();
}

int main(int argc, char **argv) {
  ros::init(argc, argv, "FT_Converter");

  std::string path = ros::package::getPath("ft_sensor");
  std::string calPath = path + "/config/FT7724.cal";
  FTConverter ft(const_cast<char *>(calPath.c_str()));

  ros::NodeHandle nh;

  ros::Publisher u3_pub = nh.advertise<std_msgs::Float32MultiArray>(
      "/force_torque_sensor/readings", 1000);
  ros::Subscriber u3Sub = nh.subscribe("/force_torque_sensor_raw/u3", 1000,
                                       &FTConverter::u3Callback, &ft);
  ros::Subscriber adcSub = nh.subscribe("/force_torque_sensor_raw/adc", 1000,
                                        &FTConverter::adcCallback, &ft);

  int count = 0;
  ros::Rate loop_rate(250);

  // wait 2 seconds before initialize the bias
  while (ros::ok()) {
    ros::spinOnce();

    count++;
    if (count == 2000) {
      ft.initBias();
      break;
    }
    loop_rate.sleep();
  }

  // after initialization, publish force torque measurement at given rate
  std::array<float, 6> ForceTorque;
  while (ros::ok()) {
    std_msgs::Float32MultiArray msg;
    msg.layout.dim.push_back(std_msgs::MultiArrayDimension());
    msg.layout.dim[0].size = 6;
    msg.layout.dim[0].stride = 1;
    msg.layout.dim[0].label = "FTReading";

    ft.getMeasurement(ForceTorque);
    msg.data.clear();
    msg.data.assign(ForceTorque.data(), ForceTorque.data() + 6);
    u3_pub.publish(msg);
    ros::spinOnce();
    loop_rate.sleep();
  }

  return 0;
}
