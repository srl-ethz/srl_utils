#!/usr/bin/env python

import rospy
import serial
from geometry_msgs.msg import Quaternion
from visualization_msgs.msg import Marker

# Configure the serial connections
ser = serial.Serial(
    port='/dev/ttyACM1',  # Change this to your serial port
    baudrate=115200,
)

# Initialize ROS Node
rospy.init_node('quaternion_visualization')

# Publisher for the Marker message for rviz
marker_pub = rospy.Publisher('visualization_marker', Marker, queue_size=10)

def publish_marker(quaternion):
    marker = Marker()
    marker.header.frame_id = "map"
    marker.type = marker.CUBE
    marker.action = marker.ADD
    marker.scale.x = 0.2
    marker.scale.y = 0.2
    marker.scale.z = 0.2
    marker.color.a = 1.0
    marker.color.r = 1.0
    marker.color.g = 0.0
    marker.color.b = 0.0
    marker.pose.orientation = quaternion

    marker_pub.publish(marker)

def read_quaternion():
    while not rospy.is_shutdown():
        if ser.inWaiting():
            data = ser.readline().decode().strip()  # Read data from serial port
            q = data.split(',')
            if len(q) == 4:  # Check if we have 4 components
                quaternion = Quaternion()
                quaternion.x = float(q[1])
                quaternion.y = float(q[2])
                quaternion.z = float(q[3])
                quaternion.w = float(q[0])

                publish_marker(quaternion)

if __name__ == '__main__':
    try:
        read_quaternion()
    except rospy.ROSInterruptException:
        pass