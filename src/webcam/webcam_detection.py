import time

import cv2
import numpy as np
from detector import Detector
from webcam_streamer import (disable_auto_focus, enable_auto_focus, set_focus,
                             webCamStreamer)


def main():
    camera_id = 4
    enable_auto_focus(camera_id)
    disable_auto_focus(camera_id)
    set_focus(camera_id, 60)
    
    detector = Detector()
    streamer = webCamStreamer(camera_id)

    # Parameters for detection
    detector.set_radii_range(12, 20)
    detector.set_param2_kpt(30)  
    detector.set_min_dist(25)
    detector.set_hough_line_threshold(6)
    num_marker = 10
    # wait one second for webcam to start
    time.sleep(1)
    
    # limit the excution speed as the max frame rate of webcam are 30 Hz
    # image_update_rate = rospy.Rate(30)

    try:
        while True: 
            # t1 = time.time()
            image = streamer.get_frame()
            detector.set_image(image)
            img, length  = detector.detect_kpt(num_marker)
            # If all the markers are detected, get center coordinates
            if length == num_marker:  
                center_x_list = detector.get_center_x_list()
                center_y_list = detector.get_center_y_list()
            # t2 = time.time()
            # print(f"detection loop {t2-t1}")
            # image_update_rate.sleep()
            
            # Display detection results
            cv2.namedWindow("webcam", cv2.WINDOW_NORMAL)
            cv2.imshow("webcam", img)
            cv2.waitKey(3)    
    finally:
        streamer.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()  

