import os
import tkinter as tk
from tkinter import ttk

class FileManager:
    def __init__(self, app):
        self.app = app
        self.current_directory = os.path.expanduser("~")

    def populate_file_tree(self, path):
        self.app.file_tree.delete(*self.app.file_tree.get_children())
        self.add_directory_to_tree('', path)

    def add_directory_to_tree(self, parent, path):
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    folder = self.app.file_tree.insert(parent, 'end', text=item, open=False)
                    self.add_directory_to_tree(folder, full_path)  # Recursión para subdirectorios
                elif item.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heic', '.heif')):
                    self.app.file_tree.insert(parent, 'end', text=item, values=(full_path,))
        except PermissionError:
            pass  # If we do not have permission to read a folder, we ignore it.

    def load_images_from_folder(self, folder_path):
        self.app.images = []
        # Iterate over the files in the folder, but only image files
        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heic', '.heif')):
                    self.app.images.append(os.path.join(root_dir, file))
        self.app.images.sort()
        self.app.current_image_index = 0
        if self.app.images:
            self.app.image_viewer.load_image(self.app.images[0])
        else:
            tk.messagebox.showinfo("Information", "No images were found in the selected folder.")

