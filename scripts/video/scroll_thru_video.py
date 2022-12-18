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
    required=True,
)
@click.option("--fps", default=30, help="Frames per second.")
def scroll_thru_video(filepath: str, fps: int):
    """Scroll through a video using trackbars.

    Args:
        filepath (str): Video filepath.
        fps (int): Frames per second.
    """
    cap = cv2.VideoCapture(filepath)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    win_title = f"Video - {filepath} @ {fps} fps"

    clip_to_range = lambda val: min(length - 1, max(0, val))

    def on_change(trackbar_value: int):
        trackbar_value = clip_to_range(trackbar_value)
        cap.set(cv2.CAP_PROP_POS_FRAMES, trackbar_value)
        # Read the frame at the current position
        err, img = cap.read()  # pylint: disable=unused-variable
        cv2.imshow(win_title, img)

    cv2.namedWindow(win_title, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("start", win_title, 0, length, on_change)
    cv2.createTrackbar("end", win_title, length, length, on_change)

    on_change(0)
    cv2.waitKey()

    start = clip_to_range(cv2.getTrackbarPos("start", win_title))
    end = clip_to_range(cv2.getTrackbarPos("end", win_title))

    wait_time = int(1000.0 / fps)
    if start >= end:
        raise Exception(f"start: {start} must be less than end: {end}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    while cap.isOpened():
        err, img = cap.read()
        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            break
        cv2.imshow(win_title, img)
        key_ESC = 27  # ASCII code for ESC
        key_pressed = cv2.waitKey(wait_time) & 0xFF
        if key_pressed == key_ESC:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    scroll_thru_video()
