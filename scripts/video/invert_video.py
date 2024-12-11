#!/Users/gavin/opt/miniforge3/bin/python3

import os
import sys

import cv2

if len(sys.argv) < 2:
    print(
        "Please provide the path to the MP4 video as a command-line argument."
    )
    sys.exit(1)

video_path = sys.argv[1]

# Get the directory and filename
directory, filename = os.path.split(video_path)
name, ext = os.path.splitext(filename)

# Create the output filename
output_filename = os.path.join(directory, f"{name}-inverted{ext}")

# Open the video
cap = cv2.VideoCapture(video_path)

# Get the video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create the video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

# Process each frame and write the inverted frame to the output video
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Invert the colors of the frame
    inverted_frame = cv2.bitwise_not(frame)

    # Write the inverted frame to the output video
    out.write(inverted_frame)

# Release the video capture and writer
cap.release()
out.release()

print(f"Inverted video saved as: {output_filename}")
