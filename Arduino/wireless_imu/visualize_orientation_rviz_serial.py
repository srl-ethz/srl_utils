#!/usr/bin/env python

import rospy
import serial
from geometry_msgs.msg import Quaternion, QuaternionStamped, TwistStamped
from visualization_msgs.msg import Marker

"""
minimal script to receive quaternion data from Arduino and visualize it in rviz
add the /visualization_marker topic in rviz
"""

# Initialize ROS Node
rospy.init_node("quaternion_visualization")

# Publisher for the Marker message for rviz
marker_pub = rospy.Publisher("visualization_marker", Marker, queue_size=10)
quatstamped_pub = rospy.Publisher("imu/quat", QuaternionStamped, queue_size=10)
twiststamped_pub = rospy.Publisher("imu/gyro", TwistStamped, queue_size=10)


def publish_QuaternionStamped(qw, qx, qy, qz):
    msg = QuaternionStamped()
    msg.header.stamp = rospy.Time.now()
    msg.quaternion.w = qw
    msg.quaternion.x = qx
    msg.quaternion.y = qy
    msg.quaternion.z = qz
    quatstamped_pub.publish(msg)


def publish_TwistStamped(gyro_x, gyro_y, gyro_z):
    msg = TwistStamped()
    msg.header.stamp = rospy.Time.now()
    msg.twist.angular.x = gyro_x
    msg.twist.angular.y = gyro_y
    msg.twist.angular.z = gyro_z
    twiststamped_pub.publish(msg)


def publish_marker(qw, qx, qy, qz):
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

    quaternion = Quaternion()
    quaternion.w = float(qw)
    quaternion.x = float(qx)
    quaternion.y = float(qy)
    quaternion.z = float(qz)

    marker.pose.orientation = quaternion

    marker_pub.publish(marker)


if __name__ == "__main__":
    # Configure the serial connections
    ser = serial.Serial(
        port="/dev/ttyACM0",  # Change this to your serial port
        baudrate=115200,
    )
    try:
        while not rospy.is_shutdown():
            if ser.inWaiting():
                data = (
                    ser.readline().decode().strip()
                )  # Read data from serial port
                q = data.split(",")
                if len(q) == 7:  # Check if we have 4 components
                    quaternion = Quaternion()
                    quaternion.x = float(q[1])
                    quaternion.y = float(q[2])
                    quaternion.z = float(q[3])
                    quaternion.w = float(q[0])
                    gyro_x = float(q[4])
                    gyro_y = float(q[5])
                    gyro_z = float(q[6])

                    publish_marker(
                        quaternion.x, quaternion.y, quaternion.z, quaternion.w
                    )
    except rospy.ROSInterruptException:
        pass
