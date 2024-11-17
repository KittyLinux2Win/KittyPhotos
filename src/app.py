import tkinter as tk
import os
import webbrowser
import platform
import subprocess
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

        self.open_editor_button = ttk.Button(self.sidebar, text="Open ImageEditor", command=self.open_image_editor)
        self.open_editor_button.pack(pady=10, padx=10, fill=tk.X)

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

        self.about_button = ttk.Button(self.viewer_frame, text="About", command=self.about_app)
        self.about_button.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X)

    def open_image_editor(self):
        try:
            subprocess.Popen(["python","src/ImageEditor.py"])
        except FileNotFoundError:
            print("Error: The file ImageEditor.py could not be found.")

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
            self.update_info(image_path)

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

    def about_app(self):
        """Display information about the app in a new window."""
        import platform
        import tkinter as tk
        from tkinter import ttk

        # Create a new top-level window
        about_window = tk.Toplevel(self.root)
        about_window.title("About KittyPhotos")
        about_window.geometry("400x300")
        about_window.configure(bg="#2e3440")
        about_window.resizable(False, False)  # Disable resizing

        # Optional: Set an icon for the window
        # about_window.iconbitmap("path_to_icon.ico")

        # Title Label
        title_label = ttk.Label(
            about_window,
            text="KittyPhotos - Linux2Win",
            font=("Arial", 16, "bold"),
            background="#2e3440",
            foreground="#eceff4"
        )
        title_label.pack(pady=(20, 10))  # Add padding at the top

        # Version Information
        version_label = ttk.Label(
            about_window,
            text="Version: 1.0.0",
            background="#2e3440",
            foreground="#eceff4"
        )
        version_label.pack(pady=5)

        # License Information
        license_label = ttk.Label(
            about_window,
            text="License: MIT",
            background="#2e3440",
            foreground="#eceff4"
        )
        license_label.pack(pady=5)

        # Developer Information
        developers_label = ttk.Label(
            about_window,
            text="Developed by: KittyLinux2Win",
            background="#2e3440",
            foreground="#eceff4"
        )
        developers_label.pack(pady=5)

        # OS Information
        os_name = platform.system()
        os_version = platform.version()
        os_info = f"OS: {os_name} (Version: {os_version})"
        os_label = ttk.Label(
            about_window,
            text=os_info,
            background="#2e3440",
            foreground="#eceff4"
        )
        os_label.pack(pady=5)

        # Buttons Frame for better layout
        buttons_frame = ttk.Frame(about_window, style="TFrame")
        buttons_frame.pack(pady=20)

        # Wiki Button
        wiki_button = ttk.Button(
            buttons_frame,
            text="View Wiki",
            command=self.view_documentation
        )
        wiki_button.grid(row=0, column=0, padx=10)

        # Close Button
        close_button = ttk.Button(
            buttons_frame,
            text="Close",
            command=about_window.destroy
        )
        close_button.grid(row=0, column=1, padx=10)

        # Center the window on the screen
        about_window.update_idletasks()
        window_width = about_window.winfo_width()
        window_height = about_window.winfo_height()
        screen_width = about_window.winfo_screenwidth()
        screen_height = about_window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        about_window.geometry(f"{window_width}x{window_height}+{x}+{y}")



if __name__ == "__main__":
    root = tk.Tk()
    app = LinuxImageViewer(root)
    root.mainloop()
