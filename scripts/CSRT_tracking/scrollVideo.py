# ------------------------------------------------------------------------------
# Script for finding relevant frames for motion extraction. Use the trackbars
# to find the relevant start and end frame (note down the numbers) so they can 
# be used in the trackNboxes.py script. After selecting the start and end frames
# you can press Enter to review the range in the video. 
# 
# Code taken from Berak in: 
# https://stackoverflow.com/questions/21983062/in-python-opencv-is-there-a-way-to-quickly-scroll-through-frames-of-a-video-all
# ------------------------------------------------------------------------------

import cv2

folder = "folder_name"
file_name = "filename_without_extension"
fps = 60

N = 2   # Number of motion markers points

video_file = f"{folder}/{file_name}.mp4"


cap = cv2.VideoCapture(video_file)
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

def onChange(trackbarValue):
    cap.set(cv2.CAP_PROP_POS_FRAMES,trackbarValue)
    err,img = cap.read()
    cv2.imshow("Video", img)
    pass

cv2.namedWindow('Video')
cv2.createTrackbar( 'start', 'Video', 10, length, onChange )
cv2.createTrackbar( 'end'  , 'Video', 100, length, onChange )

onChange(0)
cv2.waitKey()

start = cv2.getTrackbarPos('start','Video')
end   = cv2.getTrackbarPos('end','Video')
if start >= end:
    raise Exception("start must be less than end")

cap.set(cv2.CAP_PROP_POS_FRAMES,start)
while cap.isOpened():
    err,img = cap.read()
    if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
        break
    cv2.imshow("Video", img)
    k = cv2.waitKey(10) & 0xff
    if k==27:
        break
