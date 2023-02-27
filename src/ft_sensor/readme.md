# ROS Node for FT Sensor
A ROS node to read ATI FT Sensor Nano17 using Labjack U3 along with two ADCs.

ATI FT sensor Nano 17 is 6-axis force torque sensor. It output 6 voltage signals. But Labjack U3 provides only 4 ADCs that meet the requirement of Nano17 output (-10V ~ 10V). Therefore, two additional ADCs is added to get the complete readings. ADCs are read using arduino.


# Prerequisite
- ROS
- pyserial
- [labjackusb](https://github.com/labjack/exodriver)

# Install
To compile, put this node in a catkin workspace, then run
```
    catkin build
```
Before run this node, source `${CATKIN_WORKSPACE}/devel/setup.bash`.

# Usage
First, connect FT sensor to Labjack U3 and ADCs according to the color map and conncect ADCs to the arduino.

| Signal | Color  | Input    |
|--------|--------|----------|
| SG0    | brown  | ADC-AIN0 |
| SG1    | yellow | ADC-AIN1 |
| SG2    | green  | U3-AIN0  |
| SG3    | blue   | U3-AIN1  |
| SG4    | violet | U3-AIN2  |
| SG5    | grey   | U3-AIN3  |

Then, connect Labjack U3 and arduino to the computer.
In order to run the node, configure the serial port in `config/param.yaml` and run 
```
    roslaunch ft_sensor ft_sensor_node.launch
```
in the command line or include `ft_sensor_node.launch` in other launch files.

# ROS Nodes
## Nodes
**`readLabjack`** opens connection to labjack U3 and publish voltage reading from U3 on topic `/force_torque_sensor_raw/u3`

**`serial_reading_node`** open connections to serial port, read serial message and publish voltage reading from ADCs to topic `/force_torque_sensor_raw/adc`

**`ftConverter`** subscribes to topic `/force_torque_sensor_raw/u3` and topic `/force_torque_sensor_raw/adc`, keeps track of the most recent voltage reading and publish force torque reading periodically to topic `/force_torque_sensor/readings`

## Topics
*`/force_torque_sensor_raw/u3`* (std_msgs::Float32MultiArray) voltage readings from labjack u3. (SG2, SG3, SG4, SG5)

*`/force_torque_sensor_raw/adc`* (std_msgs::Float32MultiArray) voltage readings from ADC. (SG0, SG1)

*`/force_torque_sensor/readings`* (std_msgs::Float32MultiArray) force torque measurement from FT sensor. (fx, fy, fz, Tx, Ty, Tz)
