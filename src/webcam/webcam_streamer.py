#! /usr/bin/env python3
"""WebCamStreamer Object, streamming images from an external webcam"""
import time
from threading import Event, Thread

import cv2
import numpy as np
from v4l2py import Device


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