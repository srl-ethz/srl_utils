#!/Users/gavin/opt/miniforge3/bin/python3

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageGrab
from tkinterdnd2 import DND_FILES, TkinterDnD
import sys

class ImageInverter:
    def __init__(self):
        self.setup_window()

    def setup_window(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Image Inverter")
        self.root.geometry("400x250")
        self.save_var = tk.BooleanVar()

        self.label = ttk.Label(self.root, text="Drag and drop an image file here\nto invert its colors.", justify=tk.CENTER)
        self.label.pack(pady=20)

        self.chk_save_as = ttk.Checkbutton(self.root, text="Choose save location for inverted image", variable=self.save_var)
        self.chk_save_as.pack(pady=10)

        self.get_from_clipboard = ttk.Button(self.root, text="Get Image from Clipboard", command=self.handle_image_from_clipboard)
        self.get_from_clipboard.pack(pady=10)

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def invert_image(self, image):
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            rgb_image = Image.merge('RGB', (r, g, b))
            inverted_image = Image.eval(rgb_image, lambda x: 255 - x)
            r, g, b = inverted_image.split()
            inverted_image = Image.merge('RGBA', (r, g, b, a))
        else:
            inverted_image = Image.eval(image, lambda x: 255 - x)
        return inverted_image

    def save_image(self, image, output_path):
        image.save(output_path)
        messagebox.showinfo("Success", f"Inverted image saved to {output_path}")

    def open_image_dialog():
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not filepath:
            return
        image = Image.open(filepath)
        return image, filepath

    def handle_image_from_clipboard(self):
        """Attempts to invert an image from the clipboard and save it."""
        image = ImageGrab.grabclipboard()
        if image:
            inverted_image = self.invert_image(image)
            output_path = self.ensure_valid_output_path()
            self.save_image(inverted_image, output_path)
        else:
            messagebox.showerror("Error", f"No image found in clipboard.")

    def handle_drop(self, event):
        """Handle the drop event for image files."""
        for filename in self.root.tk.splitlist(event.data):
            try:
                image = Image.open(filename)
                inverted_image = self.invert_image(image)
                output_path = self.ensure_valid_output_path(input_path=filename)
                self.save_image(inverted_image, output_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {filename}\n{e}")

    def ensure_valid_output_path(self, output_path=None, input_path=None):
        if not output_path:
            if not input_path or self.save_var.get():
                output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
                if not output_path:
                    raise Exception("No output path provided.")
            elif input_path:
                path_root, ext = os.path.splitext(input_path)
                output_path = f"{path_root}-inverted{ext}"
            else:
                raise Exception("No output path provided.")
        return output_path

if __name__ == "__main__":
    img_inverter = ImageInverter()
    img_inverter.root.mainloop()