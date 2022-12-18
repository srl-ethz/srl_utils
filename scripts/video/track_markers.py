# ------------------------------------------------------------------------------
# Script for tracking N manually chosen bounding boxes within video.
# Change the video file name to your target, pick the correct fps, and choose
# how many N bounding boxes are desired. These bounding box centers (markers)
# are stored in a CSV file afterwards.
# Two videos are created as well, one is the original video cut to
# [start_frame, end_frame], and the other is with the tracking bounding boxes
# displayed.
#
# OpenCV installation can sometimes have trouble with
# cv2.legacy.MultiTracker_create(), the version that worked is:
# opencv-contrib-python 4.5.2.52
# ------------------------------------------------------------------------------

import time

import cv2
import numpy as np

folder = "folder_name"
file_name = "filename_without_extension"
fps = 60

N = 2  # Number of motion markers points

# Includes both start and end frame of video.
start_frame = 10
end_frame = 100

video_file = f"{folder}/{file_name}.mp4"

cap = cv2.VideoCapture(video_file)

framenum = 0
while cap.isOpened():
    ret, frame = cap.read()
    framenum += 1
    # print(framenum)
    if framenum < start_frame:
        continue

    # Find bounding boxes
    bboxes = []
    for i in range(N):
        bboxes.append(cv2.selectROI(f"Select {i+1}-th Marker", frame))
    break
else:
    print("ERROR loading file")
cap.release()
cv2.destroyAllWindows()


# Create multiple trackers
trackers = cv2.legacy.MultiTracker_create()
for i in range(N):
    trackers.add(cv2.legacy.TrackerCSRT_create(), frame, bboxes[i])


# Tracking
cap = cv2.VideoCapture(video_file)

# Store keypoint tracked video, using MP4 format.
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
cut_movie = cv2.VideoWriter(
    f"{folder}/cut{file_name}.mp4",
    fourcc,
    fps,
    (frame.shape[1], frame.shape[0]),
)
tracked_movie = cv2.VideoWriter(
    f"{folder}/tracked_{file_name}.mp4",
    fourcc,
    fps,
    (frame.shape[1], frame.shape[0]),
)

markers = []
framenum = 0
while cap.isOpened():
    ret, frame = cap.read()
    framenum += 1
    print(framenum)
    if framenum < start_frame:
        continue
    if not ret or framenum > end_frame:
        break

    cut_movie.write(frame)
    # Give tracker new frame with minimal movement
    found, bboxes_new = trackers.update(frame)

    if not found:
        cv2.putText(
            frame,
            "One of the objects not found",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2,
        )

    for box in bboxes_new:
        topleft = (int(box[0]), int(box[1]))
        botright = (int(box[0] + box[2]), int(box[1] + box[3]))
        cv2.rectangle(frame, topleft, botright, (0, 0, 255), 2)

    curr_markers = []
    # Compute relevant values of motion marker positions
    for i in range(N):
        # Compute centers of found bounding boxes
        curr_center = np.array(
            [
                bboxes_new[i][0] + bboxes_new[i][2] / 2,
                bboxes_new[i][1] + bboxes_new[i][3] / 2,
            ]
        )
        curr_markers.append(curr_center)

    # Markers are stored as a flattened array, x then y coordinate of each point.
    markers.append(np.array(curr_markers).flatten())

    cv2.imshow("Tracker", frame)
    tracked_movie.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cut_movie.release()
tracked_movie.release()
cap.release()
cv2.destroyAllWindows()

np.savetxt(f"{folder}/markers_{file_name}.csv", markers, delimiter=",")
