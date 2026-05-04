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
        self.last_click = None  # (x, y) в координатах оригинала

        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack()

        self.load_image()

        root.bind("<Left>", self.prev_image)
        root.bind("<Right>", self.next_image)

        root.bind("1", lambda e: self.set_scale(0.5))
        root.bind("2", lambda e: self.set_scale(0.66))
        root.bind("3", lambda e: self.set_scale(1.0))

        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Button-1>", self.mouse_click)

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

        self.canvas.config(width=new_size[0], height=new_size[1])
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        if self.last_click:
            self.draw_marker()

        self.update_title()

    def set_scale(self, scale):
        self.scale = scale
        self.update_image()

    def next_image(self, event=None):
        self.index = (self.index + 1) % len(self.images)
        self.last_click = None
        self.load_image()

    def prev_image(self, event=None):
        self.index = (self.index - 1) % len(self.images)
        self.last_click = None
        self.load_image()

    def mouse_move(self, event):
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)
        self.current_coords = (x, y)
        self.update_title()

    def mouse_click(self, event):
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)

        self.last_click = (x, y)

        text = f'"x": {x}, "y": {y}'
        print(text)

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

        self.update_image()

    def draw_marker(self):
        x, y = self.last_click

        # перевод в экранные координаты
        sx = int(x * self.scale)
        sy = int(y * self.scale)

        w, h = 120, 30
        r = 10  # радиус скругления

        x1, y1 = sx, sy
        x2, y2 = sx + w, sy + h

        # фон (черный)
        self.round_rect(x1, y1, x2, y2, r, fill="black", outline="white", width=2)

        # текст
        self.canvas.create_text(
            x1 + 10, (y1 + y2) // 2,
            text="текст",
            fill="white",
            anchor="w",
            font=("Arial", 12, "bold")
        )

    def round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def update_title(self):
        filename = self.images[self.index]
        x, y = self.current_coords
        scale_percent = int(self.scale * 100)

        self.root.title(f"{filename} | scale: {scale_percent}% | x: {x}, y: {y}")


if __name__ == "__main__":
    root = tk.Tk()
    folder_path = "images"  # укажи путь

    app = ImageViewer(root, folder_path)
    root.mainloop()
