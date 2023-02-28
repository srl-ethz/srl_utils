// Copyright 2022 Sizhe Tian, Soft Robotic Lab, ETH
// Adapted from u3Stream.c from labjackusb
// Create u3Streamer class and get stream data on call
//
// Original Author: LabJack
// December 27, 2011
// read analog inputs AI0-AI4
// Requires a U3 with hardware version 1.21 or higher.

#ifndef U3STREAMER_H
#define U3STREAMER_H

#include <array>

#include "u3.h"

static const uint8 NumChannels = 4;

class u3Streamer {
 private:
  const uint8 num_channels_ = NumChannels;  // For this example to work proper,
                                            // SamplesPerPacket needs to be a
                                            // multiple of NumChannels.
  const uint8 samples_per_packet_ =
      4;  // Needs to be 25 to read multiple StreamData
          // responses in one large packet, otherwise
          // can be any value between 1-25 for 1
          // StreamData response per packet.

  HANDLE hDevice_;
  u3CalibrationInfo cali_info_;
  int dac1_enabled_;
  int packet_counter_ = 0;
  bool init_flag_ = false;

  // double stream_voltage_[num_channels_];
  // std::array<double, NumChannels> stream_voltages_;

 public:
  u3Streamer();
  ~u3Streamer();

  /**
   * @brief Sends a ConfigIO low-level command that configures the FIOs, DAC,
   * Timers and Counters for this example
   * @param  {HANDLE} hDevice     :  device handle of labjack
   * @param  {int*} isDAC1Enabled :  settings for DAC1
   * @return {int}                :  0 if successful, -1 otherwise
   */
  int ConfigIO(HANDLE hDevice, int *isDAC1Enabled);

  /**
   * @brief Sends a StreamConfig low-level command to configure the stream.
   * @param  {HANDLE} hDevice :  device handle of labjack
   * @return {int}            :   0 if successful, -1 otherwise
   */
  int StreamConfig(HANDLE hDevice);

  /**
   * @brief Sends a StreamStart low-level command to start streaming.
   * @param  {HANDLE} hDevice :  device handle of labjack
   * @return {int}            :   0 if successful, -1 otherwise
   */
  int StreamStart(HANDLE hDevice);

  /**
   *  @brief Reads the StreamData low-level function response in a loop.  All
   * voltages from the stream are stored in the voltages 2D array.
   * @param  {HANDLE} hDevice              :   device handle of labjack
   * @param  {u3CalibrationInfo*} caliInfo :   Calibration info
   * @param  {int} isDAC1Enabled           :   Settings for DAC1
   * @return {int}                         :   0 if successful, -1 otherwise
   */
  int StreamData(HANDLE hDevice, u3CalibrationInfo *caliInfo,
                 int isDAC1Enabled);

  /**
   * @brief Sends a StreamStop low-level command to stop streaming.
   * @param  {HANDLE} hDevice :  device handle of labjack
   * @return {int}            :   0 if successful, -1 otherwise
   */
  int StreamStop(HANDLE hDevice);

  /**
   * Reads the StreamData on call, data will be saved in a std array voltages
   * @param  {std::array<double, NumChannels>} voltages :  measured voltage
   * @return {int}                         :   0 if successful, -1 otherwise
   */
  int getStreamData(std::array<double, NumChannels> &voltages);
  /**
   *
   * @return {bool}  :  flag indicating whether the labjack is initialized
   */
  bool isInit();

  /**
   * @brief A wrapper to call StreamData() function;
   */
  void stream();
};

#endif  // U3STREAMER_H
