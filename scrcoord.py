#!/usr/bin/python3

import os
import re
import tkinter as tk
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root, folder):
        self.root = root
        self.folder = folder

        self.images = self.load_images_sorted(folder)
        self.index = 0
        self.scale = 1.0
        self.current_coords = (0, 0)

        self.label = tk.Label(root)
        self.label.pack()

        self.load_image()

        root.bind("<Left>", self.prev_image)
        root.bind("<Right>", self.next_image)

        root.bind("1", lambda e: self.set_scale(0.5))
        root.bind("2", lambda e: self.set_scale(0.66))
        root.bind("3", lambda e: self.set_scale(1.0))

        self.label.bind("<Motion>", self.mouse_move)
        self.label.bind("<Button-1>", self.mouse_click)

    def load_images_sorted(self, folder):
        files = [f for f in os.listdir(folder)
                 if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))]

        def extract_number(filename):
            match = re.search(r'(\d+)(?=\.[^.]+$)', filename)
            return int(match.group(1)) if match else -1

        return sorted(files, key=extract_number)

    def load_image(self):
        path = os.path.join(self.folder, self.images[self.index])
        self.original_image = Image.open(path)
        self.update_image()

    def update_image(self):
        w, h = self.original_image.size
        new_size = (int(w * self.scale), int(h * self.scale))
        resized = self.original_image.resize(new_size)

        self.tk_image = ImageTk.PhotoImage(resized)
        self.label.config(image=self.tk_image)

        self.update_title()

    def set_scale(self, scale):
        self.scale = scale
        self.update_image()

    def next_image(self, event=None):
        self.index = (self.index + 1) % len(self.images)
        self.load_image()

    def prev_image(self, event=None):
        self.index = (self.index - 1) % len(self.images)
        self.load_image()

    def mouse_move(self, event):
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        self.current_coords = (x, y)
        self.update_title()

    def mouse_click(self, event):
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)

        text = f'"x": {x}, "y": {y}'
        print(text)

        # Копирование в буфер обмена
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # важно для clipboard

    def update_title(self):
        filename = self.images[self.index]
        x, y = self.current_coords
        scale_percent = int(self.scale * 100)

        title = f"{filename} | scale: {scale_percent}% | x: {x}, y: {y}"
        self.root.title(title)


if __name__ == "__main__":
    root = tk.Tk()

    folder_path = "images"  # укажи свою папку

    app = ImageViewer(root, folder_path)

    root.mainloop()
