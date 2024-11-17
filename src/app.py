import tkinter as tk
import os
import webbrowser
from tkinter import ttk, filedialog, messagebox
from image_viewer import ImageViewer
from file_manager import FileManager

class LinuxImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("KittyPhotos - Linux2Win")
        self.root.geometry("1024x768")
        self.root.configure(bg="#2e3440")
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, '..', 'icon', 'kitty.app.png')
        icon = tk.PhotoImage(file=icon_path)
        self.root.iconphoto(True, icon)

        self.current_image_index = 0
        self.images = []
        self.current_directory = os.path.expanduser("~")
        self.zoom_factor = 1.0
        self.is_gif = False
        self.gif_frames = []
        self.current_frame = 0
        self.photo = None

        self.setup_styles()
        self.create_widgets()

        self.image_viewer = ImageViewer(self)
        self.file_manager = FileManager(self)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TFrame", background="#2e3440")
        self.style.configure("TButton", background="#4c566a", foreground="#eceff4", padding=5)
        self.style.map("TButton", background=[('active', '#5e81ac')])
        self.style.configure("TLabel", background="#2e3440", foreground="#eceff4")
        self.style.configure("Treeview", background="#3b4252", foreground="#eceff4", fieldbackground="#3b4252")
        self.style.map("Treeview", background=[('selected', '#5e81ac')])
        self.style.configure("TScrollbar", background="#4c566a", troughcolor="#2e3440")

    def create_widgets(self):
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(self.main_paned)
        self.main_paned.add(self.sidebar, weight=1)

        self.folder_button = ttk.Button(self.sidebar, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(pady=10, padx=10, fill=tk.X)

        self.file_tree = ttk.Treeview(self.sidebar, selectmode="browse", show="tree")
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_tree_scroll = ttk.Scrollbar(self.sidebar, orient="vertical", command=self.file_tree.yview)
        self.file_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.configure(yscrollcommand=self.file_tree_scroll.set)

        self.file_tree.bind('<<TreeviewSelect>>', self.on_select)

        self.viewer_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.viewer_frame, weight=3)

        self.canvas = tk.Canvas(self.viewer_frame, bg="#2e3440", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.viewer_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.zoom_in_button = ttk.Button(self.control_frame, text="Zoom in", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.zoom_out_button = ttk.Button(self.control_frame, text="Zoom out", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.rotate_button = ttk.Button(self.control_frame, text="Rotate", command=self.rotate_image)
        self.rotate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.info_label = ttk.Label(self.control_frame, text="No image selected")
        self.info_label.pack(side=tk.RIGHT, padx=5, pady=5)

        self.documentation_button = ttk.Button(self.viewer_frame, text="View Wiki", command=self.view_documentation)
        self.documentation_button.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X)

    def update_info(self, image_path):
        """Updates the information displayed in the 'info_label' tag."""
        image_name = os.path.basename(image_path)
        self.info_label.config(text=f"Image: {image_name}")

    def select_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_directory)
        if folder_path:
            self.current_directory = folder_path
            self.file_manager.populate_file_tree(folder_path)
            self.file_manager.load_images_from_folder(folder_path)

    def on_select(self, event):
        selected_item = self.file_tree.selection()[0]
        item_values = self.file_tree.item(selected_item, 'values')
        if item_values:
            image_path = item_values[0]
            self.image_viewer.load_image(image_path)
            self.update_info(image_path)  # We call update_info to update the label

    def zoom_in(self):
        self.image_viewer.zoom_in()

    def zoom_out(self):
        self.image_viewer.zoom_out()

    def rotate_image(self):
        self.image_viewer.rotate_image()

    def view_documentation(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_path, 'html', 'wiki.html')

        if os.path.exists(html_path):
            webbrowser.open(f'file://{html_path}')
        else:
            messagebox.showerror("Error", "Wiki file not found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinuxImageViewer(root)
    root.mainloop()
