import cv2
from PIL import Image
import numpy as np
import argparse

def video2imagesequence(video_path, interval_seconds, top_left_corner, crop_size):
    """
    Extracts images from a video at a specific interval and crops them to a specified size. Also saves a tiled image.
    Useful for showing experiments in papers.
    to get the required libraries:
    pip install opencv-python-headless pillow

    :param video_path: Path to the video file.
    :param interval_seconds: Interval in seconds at which to extract images.
    :param top_left_corner: Tuple specifying the top-left corner (x, y) of the crop area.
    :param crop_size: Tuple specifying the crop size (width, height).
    """
    print(f"Extracting images from {video_path} at {interval_seconds} second intervals \
           and cropping to {crop_size} starting from {top_left_corner}")
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second of the video
    frame_interval = int(fps * interval_seconds)

    current_frame = 0
    image_count = 0
    images = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Extract and save the image at the defined interval
        if current_frame % frame_interval == 0:
            # Convert the frame from BGR to RGB color space
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)

            # Crop the image
            left, top = top_left_corner
            right = left + crop_size[0]
            bottom = top + crop_size[1]
            pil_image_cropped = pil_image.crop((left, top, right, bottom))
            images.append(pil_image_cropped)

            # Save the cropped image
            output_path = f"image_{image_count:04d}.jpg"
            pil_image_cropped.save(output_path)
            print(f"Saved {output_path}")
            image_count += 1

        current_frame += 1

    cap.release()
    print(f"Extracted and saved {image_count} images.")

    # Create a tiled image
    tiled_image = np.hstack(images)
    tiled_image = cv2.cvtColor(tiled_image, cv2.COLOR_RGB2BGR)
    tiled_image_path = "tiled_image.jpg"
    cv2.imwrite(tiled_image_path, tiled_image)
    print(f"Saved tiled image: {tiled_image_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and crop images from a video.")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("interval_seconds", type=int, help="Interval in seconds at which to extract images")
    parser.add_argument("top_left_x", type=int, help="X coordinate (i.e. distance from left edge) of the top-left corner of the crop area")
    parser.add_argument("top_left_y", type=int, help="Y coordinate (i.e. distance from top edge) of the top-left corner of the crop area")
    parser.add_argument("crop_width", type=int, help="Width of the crop area")
    parser.add_argument("crop_height", type=int, help="Height of the crop area")

    args = parser.parse_args()

    top_left_corner = (args.top_left_x, args.top_left_y)
    crop_size = (args.crop_width, args.crop_height)

    video2imagesequence(args.video_path, args.interval_seconds, top_left_corner, crop_size)
