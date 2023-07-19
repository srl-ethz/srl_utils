#!/usr/bin/env python

"""
minimal script to receive quaternion and rotational velocity data from Arduino over BLE and visualize it in rviz
add the /visualization_marker topic in rviz
"""

import asyncio, logging
import time
from ble_serial.bluetooth.ble_interface import BLE_interface
from ble_serial.scan import main as scanner

import struct

from visualize_orientation_rviz_serial import publish_marker, publish_QuaternionStamped, publish_TwistStamped

msg_time = time.time()

# callback for BLE_interface
def receive_callback(value: bytes):
    # print(f"Received [{len(value)}]: {value}")
    time_start = time.time()
    try:
        # Byte-aligned data
        # H: unsigned short (2 bytes)
        # f: float (4 bytes)
        # <: little-endian
        raw_data = struct.unpack('<H' + 'f' * 7 + 'H', value)
    except struct.error as err:
        print(f"Failed to unpack data: {err}. Raw data: {value}")
        return

    try:
        start_byte, qw, qx, qy, qz, gyro_x, gyro_y, gyro_z, end_byte = raw_data
    except ValueError as err:
        print(f"Failed to unpack data: {err}. Unpacked struct data: {raw_data}")
        return

    if start_byte != 0xFCFD or end_byte != 0xFAFB:
        print(f"Invalid start/end bytes: {start_byte}, {end_byte}")
        return

    global msg_time
    time_now = time.time()
    # print(f"[{time_now-msg_time:.4}][{time_now-time_start:.4}] Quaternion: {qw}, {qx}, {qy}, {qz} | Gyro: {gyro_x}, {gyro_y}, {gyro_z}")
    msg_time = time_now

    publish_marker(qw, qx, qy, qz)
    publish_QuaternionStamped(qw, qx, qy, qz)
    publish_TwistStamped(gyro_x, gyro_y, gyro_z)

async def main():
    ### general scan
    ADAPTER = "hci0"
    SCAN_TIME = 5  # seconds
    SERVICE_UUID = None  # optional filtering

    devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)

    target_name = "IMUGacha"
    target_id = None

    # find the device id of the target device
    is_found = False
    for device_id, info in devices.items():
        if info[0].name == target_name:
            print(f"Found {info[0].name}!")
            target_id = device_id
            is_found = True
            break
    if not is_found:
        print(f"Could not find {target_name}!")
        return

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
    # asyncio.run(main())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted by user')