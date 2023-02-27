#! /usr/bin/env python3
"""
ROS Node to process serial input and publish corresponding messages
  (2 ADC voltage readings)

  Author :  Sizhe Tian (sitian@student.ethz.ch)
  Nov 2022

"""

from curses import baudrate
from threading import Lock

import rospy
import serial
from std_msgs.msg import Float32MultiArray, MultiArrayDimension


def read_serial_node(serial_port, serial_baudrate):
    """Read serial port and publish data from it
    Serial output format:
    "[Xf.f,f.f, ...]"
        - Start with '['
        - End with ']\n'
        - First letter X represent measurement type
        - f.f measured results, float number
    Args:
        port (string): serial port name
        baudrate (int): baudrate for serial port
    """

    rospy.init_node("serial_reading_node", anonymous=True)

    ser_lock = Lock()

    print(
        f"About to init connection to serial port: {serial_port} \
                        with baudrate: {serial_baudrate}"
    )
    ser = serial.Serial(serial_port, serial_baudrate, timeout=1)

    with ser_lock:
        ser.flushInput()
        ser.flushOutput()
    measurement_type = ""
    measurement_type += "V"

    pub_voltage = rospy.Publisher(
        "/force_torque_sensor_raw/adc", Float32MultiArray, queue_size=10
    )
    msg_voltage = Float32MultiArray()
    msg_voltage.layout.dim.append(MultiArrayDimension())
    msg_voltage.layout.dim[0].size = 2
    msg_voltage.layout.dim[0].stride = 1
    msg_voltage.layout.dim[0].label = "voltages_adc"

    if not measurement_type:
        print("please specify measurement type")
        return

    print("Read serial node started")
    rate = rospy.Rate(300)
    while not rospy.is_shutdown():
        with ser_lock:
            ser.flush()  # flush serial port to get most recent sensor reading
            try:
                line = ser.readline().decode("utf8")
            except UnicodeDecodeError:
                line = ""
                print("Error reading serial messages")
        # process serial input and publish messages
        if len(line) > 4 and line[0] == "[" and line[-2] == "]":
            data_string = line[1:-2]
            m_type = data_string[0]
            data = data_string[1:].strip().split(",")
            data_list = list(map(float, data))

            if m_type == "V":
                if len(data_list) == msg_voltage.layout.dim[0].size:
                    msg_voltage.data = [data_list[0], data_list[1]]
                    pub_voltage.publish(msg_voltage)
                else:
                    print(
                        f"Length of serial message {len(data_list)} \
                        didn't match desired length {msg_voltage.layout.dim[0].size}"
                    )
            else:
                print(f"Measurement type not recognizable: {m_type}")
        else:
            print(f"Error processing line: #{line}#")
        rate.sleep()


if __name__ == "__main__":
    try:
        if rospy.has_param("/ft_sensor/port"):
            port = rospy.get_param("/ft_sensor/port")
        else:
            rospy.logerr("Please set port in launch file")
        if rospy.has_param("/ft_sensor/baudrate"):
            baudrate = rospy.get_param("/ft_sensor/baudrate")
        else:
            rospy.logerr("Please set baudrate in launch file")

        read_serial_node(port, baudrate)

    except rospy.ROSInterruptException:
        rospy.logerr("ROS Interrupt Exceptions")
