/*
  intended for Arduino nano 33 BLE board
  read from IMU, do sensor fusion, and send quaternion over serial (TODO: over BLE)
  sensor fusion: https://github.com/aster94/SensorFusion
  reading from sensor: https://github.com/arduino-libraries/Arduino_LSM9DS1
*/

#include <Arduino_LSM9DS1.h>
#include "SensorFusion.h"

void setup()
{
  Serial.begin(9600);
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

  if (IMU.accelerationAvailable())
  {
    IMU.readAcceleration(ax, ay, az); // units in g's
    // convert to m/s^2
    ax *= 9.80665;
    ay *= 9.80665;
    az *= 9.80665;
  }
  if (IMU.gyroscopeAvailable())
  {
    IMU.readGyroscope(gx, gy, gz); // units degrees / second
    // convert to rads / s
    gx *= 3.14159 / 180.0;
    gy *= 3.14159 / 180.0;
    gz *= 3.14159 / 180.0;
  }
  if (IMU.magneticFieldAvailable())
  {
    IMU.readMagneticField(mx, my, mz); // units uT
  }
  deltat = fusion.deltatUpdate();

  fusion.MadgwickUpdate(gx, gy, gz, ax, ay, az, mx, my, mz, deltat);

  quatPtr = fusion.getQuat();
  for (int i = 0; i < 4; i++)
  {
    Serial.print(quatPtr[i]);
    Serial.print("\t");
  }
  Serial.println();
}
