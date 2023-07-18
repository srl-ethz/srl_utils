#!/usr/bin/env python

import rospy
import serial
from geometry_msgs.msg import Quaternion
from visualization_msgs.msg import Marker

"""
minimal script to receive quaternion data from Arduino and visualize it in rviz
add the /visualization_marker topic in rviz
"""

# Initialize ROS Node
rospy.init_node('quaternion_visualization')

# Publisher for the Marker message for rviz
marker_pub = rospy.Publisher('visualization_marker', Marker, queue_size=10)

def publish_marker(quaternion):
    marker = Marker()
    marker.header.frame_id = "map"
    marker.type = marker.CUBE
    marker.action = marker.ADD
    # try to match dimension of Arduino
    marker.scale.x = 0.044
    marker.scale.y = 0.018
    marker.scale.z = 0.005
    marker.color.a = 1.0
    marker.color.r = 1.0
    marker.color.g = 0.0
    marker.color.b = 0.0
    marker.pose.orientation = quaternion

    marker_pub.publish(marker)


if __name__ == '__main__':
    # Configure the serial connections
    ser = serial.Serial(
        port='/dev/ttyACM0',  # Change this to your serial port
        baudrate=115200,
    )
    try:
        while not rospy.is_shutdown():
            if ser.inWaiting():
                data = ser.readline().decode().strip()  # Read data from serial port
                q = data.split(',')
                if len(q) == 7:  # Check if we have 4 components
                    quaternion = Quaternion()
                    quaternion.x = float(q[1])
                    quaternion.y = float(q[2])
                    quaternion.z = float(q[3])
                    quaternion.w = float(q[0])
                    gyro_x = float(q[4])
                    gyro_y = float(q[5])
                    gyro_z = float(q[6])

                    publish_marker(quaternion)
    except rospy.ROSInterruptException:
        pass