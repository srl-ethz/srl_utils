/*
  written for Arduino nano 33 BLE board
  read from IMU, do sensor fusion, and send quaternion (wxyz) over serial (TODO: over BLE)
  sensor fusion: https://github.com/aster94/SensorFusion
  reading from sensor: https://github.com/arduino-libraries/Arduino_LSM9DS1
  if you want really accurate measurements, calibrate the sensor following https://github.com/FemmeVerbeek/Arduino_LSM9DS1
*/

#include <Arduino_LSM9DS1.h>
#include "SensorFusion.h"

void setup()
{
  Serial.begin(115200);
  while (!Serial)
    ;

  if (!IMU.begin())
  {
    Serial.println("Failed to initialize IMU!");
    while (1)
      ;
  }
}

float gx, gy, gz, ax, ay, az, mx, my, mz;
float *quatPtr;
float deltat;
SF fusion;

void loop()
{

  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable())
  {
    IMU.readAcceleration(ax, ay, az); // units in g's
    // convert to m/s^2
    ax *= 9.80665;
    ay *= 9.80665;
    az *= 9.80665;

    IMU.readGyroscope(gx, gy, gz); // units degrees / second
    // convert to rads / s
    gx *= 3.14159 / 180.0;
    gy *= 3.14159 / 180.0;
    gz *= 3.14159 / 180.0;

  deltat = fusion.deltatUpdate();

    // sensor has left hand coordinate system for some reason, so negate y here
    fusion.MadgwickUpdate(gx, -gy, gz, ax, -ay, az, deltat);
    quatPtr = fusion.getQuat();

    // print with 4 decimal places
    Serial.print(quatPtr[0], 4);
    Serial.print(",");
    Serial.print(quatPtr[1], 4);
    Serial.print(",");
    Serial.print(quatPtr[2], 4);
    Serial.print(",");
    Serial.println(quatPtr[3], 4);

    // print the raw sensor values, may be helpful for debugging
    // Serial.print(ax, 4);
    // Serial.print(",");
    // Serial.print(ay, 4);
    // Serial.print(",");
    // Serial.print(az, 4);
    // Serial.print(",");
    // Serial.print(gx, 4);
    // Serial.print(",");
    // Serial.print(gy, 4);
    // Serial.print(",");
    // Serial.print(gz, 4);
    // Serial.println();

  }
}
