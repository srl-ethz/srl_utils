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

  if (!bleSerial.beginAndSetupBLE("IMUGacha")) {
    while (true) {
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

    // concatenate quaternion data into a string with four decimal places
    String dataToSend = String(quatPtr[0], 4) + "," +
                        String(quatPtr[1], 4) + "," +
                        String(quatPtr[2], 4) + "," +
                        String(quatPtr[3], 4);

    bleSerial.print(quatPtr[0]);
    bleSerial.print(",");
    bleSerial.print(quatPtr[1]);
    bleSerial.print(",");
    bleSerial.print(quatPtr[2]);
    bleSerial.print(",");
    bleSerial.println(quatPtr[3]);
    // print the angular velocity too
    Serial.println("Angular velocity");
    Serial.println(gx);
    Serial.println(gy);
    Serial.println(gz);
  }
}
