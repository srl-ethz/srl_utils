# !/usr/bin/env python3

"""Track bounding boxes within video.

Usage: python3 track_markers.py -f <filepath_video> -n <num_boxes> -s <start_frame> -e <end_frame>

Example: python3 track_markers.py -f ~/Downloads/tracking/vid.mp4 -n 2 -s 10 -e 50

Script for tracking N manually chosen bounding boxes within video. Point this script to the video file you would like to track and choose how many N bounding boxes are desired. These bounding box centers (markers) are stored in a CSV file afterwards. Two videos are created as well, one is the original video cut to [start_frame, end_frame], and the other is with the tracking bounding boxes displayed. If you for some reason desire to quite the tracking earlier than end_frame, you can press q to exit out.

Note: OpenCV installation can sometimes have trouble with cv2.legacy.MultiTracker_create(), the version that worked is:
opencv-contrib-python 4.5.2.52
"""

import os
import time

from typing import List
import click
import cv2
import numpy as np
import csv
import random
import pandas as pd
from datetime import datetime
import json

@click.command()
@click.option(
    "--filepath_video",
    "-fv",
    help="Video filepath. Output files will also be stored in its folder.",
    required=True,
)
@click.option("--filepath_intr_matrix", "-fm", default=None, help="Intrinsic Matrix csv filepath.",
)
@click.option(
    "--manual_input_intr_matrix",
    "-mm",
    default=None,
    nargs=9,
    type=float,
    help="""Intrinsic Matrix manual input in format 1 2 3 4 5 6 7 8 9
    --> [[1 2 3]
         [4 5 6]
         [7 8 9]]""",
)
@click.option("--num_boxes", "-n", default=2, help="Number of bounding boxes."
)
@click.option(
    "--start_frame", "-s", default=0, help="Relevant starting frame of video."
)
@click.option(
    "--end_frame", "-e", default=100, help="Relevant ending frame of video."
)
@click.option(
    "--depth", "-d", default=1, help="Image depth."
)
@click.option(
    "--frames_per_second", "-fps", default=240, help="Frames per second of Video (240 FPS Default for iPhone Slow Motion)"
)

@click.option(
    "--save_intr_matrix", "-sm", is_flag=True, default=False, help="Save Matrix to workspace --> dont need -m tag anymore"
)


def track_markers(
    filepath_video: str, filepath_intr_matrix: str, manual_input_intr_matrix: List[float], num_boxes: int, start_frame: int, end_frame: int, depth: int, frames_per_second: int, save_intr_matrix):
    """Track bounding boxes within video.
    Script for tracking N manually chosen bounding boxes within video. Point this script to the video file you would like to track and choose how many N bounding boxes are desired. These bounding box centers (markers) are stored in a CSV file afterwards. Two videos are created as well, one is the original video cut to [start_frame, end_frame], and the other is with the tracking bounding boxes displayed

    Args:
        filepath_video (str): Video filepath.
        filepath_intr_matrix (str): Intrinsic Matrix filepath.
        manual_input_matrix (9 floats): Manually input Intrinsic Matrix.
        num_boxes (int): Number of bounding boxes.
        start_frame (int): Starting frame of video at which tracking should start.
        end_frame (int): Last frame of video that should be considered (inclusive) during tracking.
        frames_per_second (int): frames per seconds of recorded Video.
        save_intrinsic_matrix (flag): If given, intrinsic matrix is saved to workspace where it can be used w/o utilizing the -m flag anymore.
    """

    # get intrinsic matrix of camera from either csv file or direct terminal input
    if filepath_intr_matrix and manual_input_intr_matrix:
        raise ValueError("Only one of filepath_intr_matrix (-fm) or manual_input_intr_matrix (-mm) should be provided.")
    if manual_input_intr_matrix:
        intr_matrix = np.array(manual_input_intr_matrix).reshape(3, 3)
    else:
        if filepath_intr_matrix:
            print("Loading intrinsic matrix from: " + filepath_intr_matrix) 
        else:
            filepath_intr_matrix = 'matrix.csv'
            print("Loading intrinsic matrix from: " + filepath_intr_matrix) 


        intr_matrix_data = []
        with open(filepath_intr_matrix, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                intr_matrix_data.append(row)
        intr_matrix = np.array(intr_matrix_data, dtype=float)

    # save intrinsic matrix in workspace
    if(save_intr_matrix):
        print("Saving intrinsic matrix to Workspace")
        df_intr_matrix = pd.DataFrame(intr_matrix)
        df_intr_matrix.to_csv('matrix.csv', header=False, index=False)


    folder = os.path.dirname(filepath_video)
    video_name = os.path.basename(filepath_video)
    cap = cv2.VideoCapture(filepath_video)

    framenum = 0
    while cap.isOpened():
        ret, frame = cap.read()
        framenum += 1
        if framenum < start_frame:
            continue

        # Find bounding boxes
        bboxes = []
        for i in range(num_boxes):
            bboxes.append(cv2.selectROI(f"Select {i+1}-th Marker", frame))
        break
    else:
        print("ERROR loading file")
    cap.release()
    cv2.destroyAllWindows()

    # Create multiple trackers
    trackers = cv2.legacy.MultiTracker_create()
    for i in range(num_boxes):
        trackers.add(cv2.legacy.TrackerCSRT_create(), frame, bboxes[i])

    # Tracking
    cap = cv2.VideoCapture(filepath_video)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Store keypoint tracked video, using MP4 format.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    cut_movie = cv2.VideoWriter(
        f"{folder}/cut_video.mp4",
        fourcc,
        fps,
        (frame.shape[1], frame.shape[0]),
    )
    tracked_movie = cv2.VideoWriter(
        f"{folder}/tracked_video.mp4",
        fourcc,
        fps,
        (frame.shape[1], frame.shape[0]),
    )

    markers = []
    coords = []
    framenum = 0
    colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(num_boxes)]


    while cap.isOpened():
        ret, frame = cap.read()
        framenum += 1
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
                text="One of the objects not found",
                org=(20, frame.shape[0]-20),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=(0, 0, 255),
                thickness=2,
            )

        for box in bboxes_new:
            topleft = (int(box[0]), int(box[1]))
            botright = (int(box[0] + box[2]), int(box[1] + box[3]))
            cv2.rectangle(
                frame, topleft, botright, color=(0, 0, 255), thickness=2
            )

        curr_markers = []
        curr_coords = []
        org_x = 100
        org_y = 70
        vertical_spacing = 30
    
        # Compute relevant values of motion marker positions
        for i in range(num_boxes):
            # Compute centers of found bounding boxes
            curr_center = np.array(
                [
                    bboxes_new[i][0] + bboxes_new[i][2] / 2,
                    bboxes_new[i][1] + bboxes_new[i][3] / 2,
                ]
            )

            coords_2d = np.array([curr_center[0], curr_center[1], depth])
            # Compute 3D coordinates of marker position
            coords_3d = np.dot(np.linalg.inv(intr_matrix), coords_2d)

            new_y = org_y + i * vertical_spacing

            cv2.putText(
                frame,
                text=f"Marker {i+1}: " + str(coords_3d),
                org=(org_x, new_y),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.75,
                color=colors[i],
                thickness=2,
            )

            reprojected_coords_2d = np.dot(intr_matrix, coords_3d)
            cv2.drawMarker(frame, (int(reprojected_coords_2d[0]), int(reprojected_coords_2d[1])), color=colors[i], thickness=3, markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,markerSize=20)


            curr_markers.append(curr_center)
            curr_coords.append(coords_3d)
        # Markers are stored as a flattened array, x then y coordinate of each point.
        markers.append(np.array(curr_markers).flatten())
        # 3D Coordinates are stored as a flattened array, x, y then z coordinate of each point.
        coords.append(np.array(curr_coords).flatten())


        cv2.imshow("Tracker (press Q to exit early)", frame)
        tracked_movie.write(frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Exited early!")
            break

    cut_movie.release()
    tracked_movie.release()
    cap.release()
    cv2.destroyAllWindows()


    # some code to config header and csv files
    df_coords = pd.DataFrame(coords)
    df_markers = pd.DataFrame(markers)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = {'TIME': timestamp, 'FPS': frames_per_second, 'TOTAL FRAMES': end_frame-start_frame, 'TOTAL MARKERS': num_boxes, 'INTRINSIC MATRIX': intr_matrix}
    
    header_df = pd.DataFrame.from_dict(header, orient='index', columns=['Header'])
    header_df.index.name = 'Column'
    header_df.to_csv(f"{folder}/data_{video_name}_{timestamp}.csv")

    column_headers = []
    for i in range(num_boxes):
        for j, coord in enumerate(['X', 'Y', 'Z']):
            column_header = f"Marker {i+1}: {coord}-Coord"
            column_headers.append(column_header)
    df_coords.columns = column_headers
    # Save the df_coords DataFrame to a CSV file
    df_coords.to_csv(f"{folder}/coords3D_{video_name}_{timestamp}.csv", index=False)

    column_headers = []
    for i in range(num_boxes):
        for j, coord in enumerate(['X', 'Y']):
            column_header = f"Marker {i+1}: {coord}-Pos"
            column_headers.append(column_header)
    df_markers.columns = column_headers
    # Save the df_markers DataFrame to a CSV file
    df_markers.to_csv(f"{folder}/coords2D_{video_name}_{timestamp}.csv", index=False)


if __name__ == "__main__":
    track_markers()
