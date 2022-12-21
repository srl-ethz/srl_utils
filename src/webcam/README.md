# Webcam Streaming and Keypoint detection
A python script that opens a webcam (e.g. Logitech C920) and detects markers in the image. There are two components here. One create the webcam connection and update most recent frame from the webcam. Another one detect markers shown in ( ) for each frame. 

To run the detection, set camera id and parameter detections in webcam_detection.py and run 
```
python3 webcam_detecion.py
```
## Dependency
- python3
- opencv

## Webcam streaming
`webCamStreamer` class opens the webcam connections and update frame from webcam

Some small functions are defined to control the focus of webcam mannually (for camera intrinsic calibration)

## Keypoint detection
`Detector` class can accept a image and detect pixel location of markers. 