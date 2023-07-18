#!/usr/bin/env python

"""
minimal script to receive quaternion data from Arduino over BLE and visualize it in rviz
add the /visualization_marker topic in rviz
"""

import asyncio, logging

from ble_serial.bluetooth.ble_interface import BLE_interface
from ble_serial.scan import main as scanner

from geometry_msgs.msg import Quaternion

from visualize_orientation_rviz_serial import publish_marker


# Arduino sends quaternion data as a comma-separated string
# e.g. "1.0,0.0,0.0,0.0\n". This buffer holds the string until a newline is
# received, then parses the string and publishes the quaternion.
str_buffer = ""


# callback for BLE_interface
def receive_callback(value: bytes):
    global str_buffer
    str_buffer += value.decode()
    if "\n" in str_buffer:
        # parse the string and look for a newline
        newline_idx = str_buffer.index("\n")
        rx_line = str_buffer[:newline_idx]
        str_buffer = str_buffer[newline_idx + 1 :]

        # parse the line and publish the quaternion
        rx_vals_str = rx_line.split(",")
        if len(rx_vals_str) == 4:
            rx_vals = [float(x) for x in rx_vals_str]
            quaternion = Quaternion()
            quaternion.x = float(rx_vals[1])
            quaternion.y = float(rx_vals[2])
            quaternion.z = float(rx_vals[3])
            quaternion.w = float(rx_vals[0])
            publish_marker(quaternion)
            print(f"Quaternion: {quaternion}")


async def main():
    ### general scan
    ADAPTER = "hci0"
    SCAN_TIME = 5  # seconds
    SERVICE_UUID = None  # optional filtering

    devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)

    target_name = "IMUGacha"
    target_id = None

    # find the device id of the target device
    for device_id, info in devices.items():
        if info[0].name == target_name:
            print(f"Found {info[0].name}!")
            target_id = device_id
            break

    WRITE_UUID = None
    READ_UUID = None
    DEVICE = target_id

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

    try:
        await ble.connect(DEVICE, "public", 10.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "rw")

        # Sleep while the BLE interface runs in the background
        while True:
            await asyncio.sleep(1)
    finally:
        await ble.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())