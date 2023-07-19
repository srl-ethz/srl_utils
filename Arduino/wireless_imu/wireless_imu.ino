/*
  written for Arduino nano 33 BLE board
  read from IMU, do sensor fusion, and send quaternion (wxyz) and rotational velocity (rx, ry, rz in rad/s) data over serial and BLE
  sensor fusion: https://github.com/aster94/SensorFusion
  reading from sensor: https://github.com/arduino-libraries/Arduino_LSM9DS1
  if you want really accurate measurements, calibrate the sensor following https://github.com/FemmeVerbeek/Arduino_LSM9DS1
*/

#include <Arduino_LSM9DS1.h>
#include "SensorFusion.h"
#include <HardwareBLESerial.h>

struct __attribute__((packed)) packed_struct_bytearray
{
  uint16_t start_bytes_u16;
  float data[7];
  uint16_t end_bytes_u16;
};

typedef union union_struct
{
  struct packed_struct_bytearray packed
  {
  };
  uint8_t b[32];
} ufloat8x32;

HardwareBLESerial &bleSerial = HardwareBLESerial::getInstance();
bool use_wired_serial = false; // BLE is always on, wired Serial communication is enabled if the port can be opened at the beginning
void setup()
{
  Serial.begin(115200);
  for (int i = 0; i < 10e3; i++)
  {
    // try to connect to Serial port but give up if it doesn't work after many tries
    if (Serial)
    {
      use_wired_serial = true;
      break;
    }
  }

  if (!IMU.begin())
  {
    if (use_wired_serial)
      Serial.println("Failed to initialize IMU!");
    while (1)
      ;
  }

  if (!bleSerial.beginAndSetupBLE("IMUGacha"))
  {
    while (true)
    {
      if (use_wired_serial)
        Serial.println("Failed to initialize HardwareBLESerial!");
      delay(1000);
    }
  }

  // below are the calibration results from DIY_Calibration_Accelerometer/Gyroscope in https://github.com/FemmeVerbeek/Arduino_LSM9DS1
  IMU.setAccelFS(3);
  IMU.setAccelODR(5);
  IMU.setAccelOffset(-0.001554, -0.010849, -0.029102);
  IMU.setAccelSlope(1.003402, 0.998643, 1.003454);
  IMU.setGyroFS(2);
  IMU.setGyroODR(5);
  IMU.setGyroOffset(-0.094818, 0.568848, 0.406097);
  IMU.setGyroSlope(1.154223, 1.139804, 1.150908);
}

float gx, gy, gz, ax, ay, az, mx, my, mz;
float *quatPtr;
float deltat;
SF fusion;

// auto time_start = millis();

void loop()
{

  // this must be called regularly to perform BLE updates
  bleSerial.poll();

  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable())
  {

    static const float CONST_g{9.80665};
    static const float CONST_deg_to_rad{M_PI / 180.0};

    IMU.readAcceleration(ax, ay, az); // units in g's
    // convert to m/s^2
    ax *= CONST_g;
    ay *= CONST_g;
    az *= CONST_g;

    IMU.readGyroscope(gx, gy, gz); // units degrees / second
    // convert to rads / s
    gx *= CONST_deg_to_rad;
    gy *= CONST_deg_to_rad;
    gz *= CONST_deg_to_rad;

    deltat = fusion.deltatUpdate();

    // sensor has left hand coordinate system for some reason, so negate y here
    fusion.MadgwickUpdate(gx, -gy, gz, ax, -ay, az, deltat);
    quatPtr = fusion.getQuat();

    // const auto time_end = millis();

    ufloat8x32 dataToSend;
    dataToSend.packed.start_bytes_u16 = 0xFCFD;
    dataToSend.packed.data[0] = quatPtr[0];
    // time_start = time_end;
    dataToSend.packed.data[1] = quatPtr[1];
    dataToSend.packed.data[2] = quatPtr[2];
    dataToSend.packed.data[3] = quatPtr[3];
    dataToSend.packed.data[4] = gx;
    dataToSend.packed.data[5] = gy;
    dataToSend.packed.data[6] = gz;
    dataToSend.packed.end_bytes_u16 = 0xFAFB;

    if (use_wired_serial)
    {
      Serial.write(dataToSend.b, 32);
    }
    bleSerial.write_buf(dataToSend.b, 32);
  }
}
