#!/usr/bin/python3

import tkinter as tk
from tkinter import filedialog, simpledialog
import re
import pyperclip

class TemplateManager:
    def __init__(self):
        # 2 фиксированных шаблона
        # 1. "x": %d, "y": %d (с любыми пробелами/переносами)
        self.xy_regex = re.compile(r'"x"\s*:\s*(\d+)\s*,\s*"y"\s*:\s*(\d+)', re.MULTILINE)

        # 2. "%s": %d  (любой ключ)
        self.kv_regex = re.compile(r'"([^"]+)"\s*:\s*(\d+)', re.MULTILINE)

    def detect_template(self, text):
        # определяем по вставляемому тексту
        if self.xy_regex.fullmatch(text.strip()):
            return self.xy_regex

        if self.kv_regex.fullmatch(text.strip()):
            return self.kv_regex

        return None

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("TTE")
        self.filename = None
        self.modified = False

        self.text = tk.Text(root, undo=True, bg="#1e1e1e", fg="#ffffff", insertbackground="white")
        self.text.pack(fill="both", expand=True)

        self.text.bind("<<Modified>>", self.on_modified)
        self.text.bind("<Button-3>", self.show_context_menu)

        self.templates = TemplateManager()

        self.create_menu()
        self.create_context_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="Find", command=self.find_text)
        edit_menu.add_command(label="Replace", command=self.replace_text)
        edit_menu.add_command(label="Paste Template", command=self.paste_template)
        menu.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menu)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Paste Template", command=self.paste_template)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def on_modified(self, event=None):
        self.modified = True
        self.update_title()
        self.text.edit_modified(False)

    def update_title(self):
        name = self.filename if self.filename else "Untitled"
        if self.modified:
            name += " *"
        self.root.title(name)

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, f.read())
            self.filename = path
            self.modified = False
            self.update_title()

    def save_file(self):
        if not self.filename:
            self.save_as()
        else:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))
            self.modified = False
            self.update_title()

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            self.filename = path
            self.save_file()

    def find_text(self):
        query = simpledialog.askstring("Find", "Text:")
        if not query:
            return

        start = self.text.index(tk.INSERT)
        pos = self.text.search(query, start, tk.END)

        if pos:
            end = f"{pos}+{len(query)}c"
            self.text.tag_remove("found", "1.0", tk.END)
            self.text.tag_add("found", pos, end)
            self.text.tag_config("found", background="yellow", foreground="black")
            self.text.mark_set(tk.INSERT, end)
            self.text.see(pos)

    def replace_text(self):
        find = simpledialog.askstring("Find", "Find:")
        replace = simpledialog.askstring("Replace", "Replace:")
        if not find:
            return

        start = "1.0"
        while True:
            pos = self.text.search(find, start, tk.END)
            if not pos:
                break
            end = f"{pos}+{len(find)}c"
            self.text.delete(pos, end)
            self.text.insert(pos, replace)
            start = pos

    def paste_template(self):
        clip = pyperclip.paste()
        content = self.text.get("1.0", tk.END)

        regex = self.templates.detect_template(clip)
        if not regex:
            self.text.insert(tk.INSERT, clip)
            return

        cursor_index = self.text.index(tk.INSERT)
        cursor_pos = self.text.count("1.0", cursor_index, "chars")[0]

        closest_match = None
        min_distance = None

        for match in regex.finditer(content):
            start = match.start()

            # только вниз
            if start < cursor_pos:
                continue

            distance = start - cursor_pos

            if min_distance is None or distance < min_distance:
                min_distance = distance
                closest_match = match

        if closest_match:
            start = closest_match.start()
            end = closest_match.end()

            start_idx = f"1.0+{start}c"
            end_idx = f"1.0+{end}c"

            self.text.delete(start_idx, end_idx)
            self.text.insert(start_idx, clip)
        else:
            self.text.insert(tk.INSERT, clip)

if __name__ == "__main__":
    root = tk.Tk()

    try:
        root.iconbitmap("tte.ico")
    except:
        pass

    editor = TextEditor(root)
    root.mainloop()

