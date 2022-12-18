# !/usr/bin/env python3

"""Scroll through a video using trackbars.

Usage: python3 scroll_thru_video.py -f <filepath> --fps <fps>

Example: python3 scroll_thru_video.py -f ~/Downloads/vid.mp4 --fps 30

Note: The video will play at the specified fps, but the trackbars
will not update at that rate.

Script for finding relevant frames for motion extraction. Use the trackbars
to find the relevant start and end frame (note down the numbers) so they
can be used in the trackNboxes.py script. After selecting the start and
end frames press Enter to review the range in the video.

Source:
Based on the following StackOverflow answer by Berak
https://stackoverflow.com/a/21983879
"""


import click
import cv2


@click.command()
@click.option(
    "--filepath",
    "-f",
    help="Video filepath.",
)
@click.option("--fps", default=30, help="Frames per second.")
def scrollThruVideo(filepath: str, fps: int):
    """Scroll through a video using trackbars.

    Args:
        filepath (str): Video filepath.
        fps (int): Frames per second.
    """
    cap = cv2.VideoCapture(filepath)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def onChange(trackbar_value: int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, trackbar_value)
        err, img = cap.read()
        cv2.imshow("Video", img)

    cv2.namedWindow("Video")
    cv2.createTrackbar("start", "Video", 10, length, onChange)
    cv2.createTrackbar("end", "Video", 100, length, onChange)

    onChange(0)
    cv2.waitKey()

    start = cv2.getTrackbarPos("start", "Video")
    end = cv2.getTrackbarPos("end", "Video")
    wait_time = int(1000.0 / fps)
    if start >= end:
        raise Exception("start must be less than end")

    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    while cap.isOpened():
        err, img = cap.read()
        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            break
        cv2.imshow("Video", img)
        key_ESC = 27  # ASCII code for ESC
        key_pressed = cv2.waitKey(wait_time) & 0xFF
        if key_pressed == key_ESC:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    scrollThruVideo()
