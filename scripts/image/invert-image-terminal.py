#!/Users/gavin/opt/miniforge3/bin/python

import os
import argparse
from PIL import Image, ImageGrab
from tkinter import Tk, simpledialog
import sys


def invert_image(image):
    """
    Inverts the colors of a PIL Image object, handling RGBA images as well.
    """
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        inverted_image = Image.eval(rgb_image, lambda x: 255 - x)
        r, g, b = inverted_image.split()
        inverted_image = Image.merge('RGBA', (r, g, b, a))
    else:
        inverted_image = Image.eval(image, lambda x: 255 - x)
    return inverted_image

def append_to_filename(filepath, suffix):
    root, ext = os.path.splitext(filepath)
    return f"{root}{suffix}{ext}"

def save_image(image, output_path):
    """Saves the inverted image to the specified path."""
    image.save(output_path)
    print(f"Inverted image saved to {output_path}")

def handle_image_from_file(image_path, output_path=None):
    """Inverts an image from a file and saves it."""
    image = Image.open(image_path)
    if not output_path:
        root, ext = os.path.splitext(image_path)
        output_path = f"{root}-inverted{ext}"
    inverted_image = invert_image(image)
    save_image(inverted_image, output_path)

def handle_image_from_clipboard(output_path):
    """Attempts to invert an image from the clipboard and save it."""
    image = ImageGrab.grabclipboard()
    if image:
        inverted_image = invert_image(image)
        save_image(inverted_image, output_path)
    else:
        print("No image found in clipboard.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invert colors of an image.")
    parser.add_argument("-i", "--input", type=str, help="Path to the image file to be inverted.")
    parser.add_argument("-o", "--output", type=str, help="Path to save the inverted image. If not provided, prompts for input or saves with a default name.")

    args = parser.parse_args()
    if not args.output and args.input:
        args.output = append_to_filename(args.input, "-inverted")
    else:
        Tk().withdraw()  # Hide the main tkinter window
        # GUI dialog to ask for the filename directly
        args.output = simpledialog.askstring("Save As", "Enter filename for the inverted image:")
        if not args.output:
            print("No filename provided. Exiting.")
            sys.exit(1)

    if args.input:    
        handle_image_from_file(args.input, args.output)
    else:
        handle_image_from_clipboard(args.output)
