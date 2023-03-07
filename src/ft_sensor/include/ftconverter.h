// Copyright 2022 Sizhe Tian, Soft Robotic Lab, ETH
// Adapted from samples in ATI ATIDAQ F/T C Library
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

#ifndef FTCONVERTER_H
#define FTCONVERTER_H

#include <array>
#include <mutex>

#include "lib/libATIDAQ/ftconfig.h"
#include "ros/ros.h"
#include "std_msgs/Float32MultiArray.h"

class FTConverter {
 public:
  explicit FTConverter(char *calfilepath);
  ~FTConverter();
  /**
   * @brief initialize bias using current voltage reading
   *
   */
  void initBias();

  /**
   * @brief using most recent voltage results to calculate force/torque
   * measurement and saved in measurement
   * @param  {std::array<float, 6> &} measurement:
   *
   */
  void getMeasurement(std::array<float, 6> *measurement);

  /**
   * @brief Callback function for the message from labjack u3
   *    check message data dimension and saved it in voltage_
   * @param  {std_msgs::Float32MultiArray} msg :
   */
  void u3Callback(std_msgs::Float32MultiArray msg);
  
  /**
   * @brief Callback function for the message from adc
   *    check message data dimension and data input range
   *    and saved it in voltage_
   * @param  {std_msgs::Float32MultiArray} msg :
   */
  void adcCallback(std_msgs::Float32MultiArray msg);

 private:
  // std::string calfilepath_;  // path to the calibration files
  Calibration *cal_;  // struct containing calibration information
  short sts_;         // return value from functions
  bool biasInit_ = false;

  std::array<float, 6> voltages_{
      0, 0, 0, 0, 0, 0};  // array to store raw voltage measurements
  std::array<float, 6> bias_{0, 0, 0, 0, 0, 0};  // array to store bias
  std::array<float, 6> transformation_{
      0, 0, 0, 0, 0, 0};  // transform includes a translation
                          // along the Z-axis and a rotation about the X-axis.

  std::mutex voltage_mtx_;
};

#endif  // FTCONVERTER_H
