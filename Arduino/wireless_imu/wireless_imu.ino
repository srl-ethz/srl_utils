/*
  written for Arduino nano 33 BLE board
  read from IMU, do sensor fusion, and send quaternion (wxyz) over serial (TODO: over BLE)
  sensor fusion: https://github.com/aster94/SensorFusion
  reading from sensor: https://github.com/arduino-libraries/Arduino_LSM9DS1
  if you want really accurate measurements, calibrate the sensor following https://github.com/FemmeVerbeek/Arduino_LSM9DS1
*/

#include <Arduino_LSM9DS1.h>
#include "SensorFusion.h"
#include <HardwareBLESerial.h>

HardwareBLESerial &bleSerial = HardwareBLESerial::getInstance();
bool use_wired_serial = false;  // BLE is always on, wired Serial communication is enabled if the port can be opened at the beginning
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

  if (!bleSerial.beginAndSetupBLE("IMUGacha")) {
    while (true) {
      if (use_wired_serial)
        Serial.println("Failed to initialize HardwareBLESerial!");
      delay(1000);
    }
  }
}

float gx, gy, gz, ax, ay, az, mx, my, mz;
float *quatPtr;
float deltat;
SF fusion;

void loop()
{

  // this must be called regularly to perform BLE updates
  bleSerial.poll();

  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable())
  {

    static const float CONST_g {9.80665};
    static const float CONST_deg_to_rad {M_PI / 180.0};

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

    // concatenate quaternion and gyro data into a string with four decimal places
    String dataToSend = String(quatPtr[0], 4) + "," +
                        String(quatPtr[1], 4) + "," +
                        String(quatPtr[2], 4) + "," +
                        String(quatPtr[3], 4) + "," +
                        String(gx, 4) + "," +
                        String(gy, 4) + "," +
                        String(gz, 4);

    if (use_wired_serial)
      Serial.println(dataToSend);
    bleSerial.println(dataToSend.c_str());
  }
}
