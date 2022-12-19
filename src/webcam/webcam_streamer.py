#! /usr/bin/env python3
import time
from threading import Event, Thread

import cv2
import numpy as np
from v4l2py import Device


class webCamStreamer:
    def __init__(self, id) -> None: 
        self.cam = Device.from_id(id)
        self.cam.video_capture.set_format(1920, 1080, 'MJPG')

        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        
        self.webcam_stop = Event()
        self.webcam_stop.clear()

        self.thread.start()
        
    def update(self):
        while not self.webcam_stop.isSet():
            for index, frame_byte in enumerate(self.cam):
                a = frame_byte.find(b'\xff\xd8')
                b = frame_byte.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = frame_byte[a:b+2]
                    frame_byte = frame_byte[b+2:]
                    self.frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

    def get_frame(self):
        return self.frame.copy()

    def stop(self):
        self.webcam_stop.set()