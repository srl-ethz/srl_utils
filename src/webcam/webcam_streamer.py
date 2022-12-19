#! /usr/bin/env python3
"""WebCamStreamer Object, streamming images from an external webcam"""
import subprocess
import time
from threading import Event, Thread

import cv2
import numpy as np
from v4l2py import Device

# Settings for Logitech C920
# https://www.kurokesu.com/main/2016/01/16/manual-usb-camera-settings-in-linux/
#                      brightness (int)    : min=0 max=255 step=1 default=-8193 value=128
#                        contrast (int)    : min=0 max=255 step=1 default=57343 value=128
#                      saturation (int)    : min=0 max=255 step=1 default=57343 value=128
#  white_balance_temperature_auto (bool)   : default=1 value=1
#                            gain (int)    : min=0 max=255 step=1 default=57343 value=0
#            power_line_frequency (menu)   : min=0 max=2 default=2 value=2
#       white_balance_temperature (int)    : min=2000 max=6500 step=1 default=57343 value=4000 flags=inactive
#                       sharpness (int)    : min=0 max=255 step=1 default=57343 value=128
#          backlight_compensation (int)    : min=0 max=1 step=1 default=57343 value=0
#                   exposure_auto (menu)   : min=0 max=3 default=0 value=3
#               exposure_absolute (int)    : min=3 max=2047 step=1 default=250 value=250 flags=inactive
#          exposure_auto_priority (bool)   : default=0 value=1
#                    pan_absolute (int)    : min=-36000 max=36000 step=3600 default=0 value=0
#                   tilt_absolute (int)    : min=-36000 max=36000 step=3600 default=0 value=0
#                  focus_absolute (int)    : min=0 max=250 step=5 default=8189 value=0 flags=inactive
#                      focus_auto (bool)   : default=1 value=1
#                   zoom_absolute (int)    : min=100 max=500 step=1 default=57343 value=100


# useful functions to set the camera parameters
# If camera intrinsic is to be used, disable auto focus and manually set a focus 
# to make sure focus remain constant
# v4l-utils required: sudo apt install v4l-utils
def disable_auto_focus(id: int):
    subprocess.call([f'v4l2-ctl  -d {id} --set-ctrl=focus_auto=0' ], shell=True)

def enable_auto_focus(id: int):
    subprocess.call([f'v4l2-ctl  -d {id} --set-ctrl=focus_auto=1' ], shell=True)

def set_focus(id: int, focus: int):
    subprocess.call([f'v4l2-ctl  -d {id} --set-ctrl=focus_absolute={focus}' ], shell=True)



class webCamStreamer:
    """Class to interact with external webcam.
    
    A thread is running on background to retrieve the most recent image. 
    To get the most recent frame, call the function get_frame()
    
    """
    def __init__(self, id:int) -> None: 
        """Initializer

        Args:
            id (int): camera id. 0 if no other camera is avaiable. 
                      could be other value if there are integrated cameras
        """
        self.id = id
        self.cam = Device.from_id(self.id)
        # Set format of the streamming
        self.cam.video_capture.set_format(1920, 1080, 'MJPG')
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        # Event to control the thread
        self.webcam_stop = Event()
        self.webcam_stop.clear()
        # start streamming
        self.thread.start()
        
    def update(self):
        """Function that runs on another thread to update most recent frame.
        """
        while not self.webcam_stop.isSet():
            for index, frame_byte in enumerate(self.cam):
                # JPEG signiture, for details, see https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
                # ff d8: Start of Image
                # ff d9: End of Image
                a = frame_byte.find(b'\xff\xd8') 
                b = frame_byte.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = frame_byte[a:b+2]
                    frame_byte = frame_byte[b+2:]
                    # convert image string to cv2 datatype and save to the self.frame
                    self.frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

    def get_frame(self):
        """Get most recent frame

        Returns:
            cv2.Mat: copy of most recent frame 
        """
        return self.frame.copy()

    def stop(self):
        """set webcam_stop event and stop updating frames
        """
        self.webcam_stop.set()