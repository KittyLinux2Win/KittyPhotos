import tkinter as tk
import os
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageDraw


class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("KittyPhotos - Image Editor")
        self.root.geometry("1024x768")
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, '..', 'icon', 'kitty.app.png')
        icon = tk.PhotoImage(file=icon_path)
        self.root.iconphoto(True, icon)
        self.root.configure(bg="#2e3440")
        self.unsaved_changes = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.image = None
        self.photo = None
        self.file_path = None
        self.history = []  # Image state history
        self.redo_stack = []  # Redo stack
        self.zoom_factor = 1.0
        self.drawing = False
        self.draw_x = 0
        self.draw_y = 0
        self.brush_color = "#000000"
        self.brush_size = 3
        self.shape_tool = None
        self.start_shape_x = 0
        self.start_shape_y = 0
        self.crop_rectangle = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        self.setup_styles()
        self.create_widgets()

    def on_close(self):
        """Handling the window closing event."""
        if self.unsaved_changes:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?"
            )
            if response is None:
                return
            elif response:
                self.save_image()
        self.root.destroy()

    def setup_styles(self):
        """Set up custom styles."""
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

        """Create the graphical interface."""
        # Main window divided
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Left side: Tools
        self.sidebar = ttk.Frame(self.main_paned)
        self.main_paned.add(self.sidebar, weight=1)

        # Group: Files
        file_frame = ttk.Frame(self.sidebar)
        file_frame.pack(pady=10, padx=10, fill=tk.X)
        ttk.Label(file_frame, text="File", anchor="w").pack(fill=tk.X, pady=5)
        ttk.Button(file_frame, text="Open Image", command=self.open_image).pack(pady=5, fill=tk.X)
        ttk.Button(file_frame, text="Save Image", command=self.save_image).pack(pady=5, fill=tk.X)

        # Group: Basic Edits
        edit_frame = ttk.Frame(self.sidebar)
        edit_frame.pack(pady=10, padx=10, fill=tk.X)
        ttk.Label(edit_frame, text="Basic Edits", anchor="w").pack(fill=tk.X, pady=5)
        ttk.Button(edit_frame, text="Undo", command=self.undo).pack(pady=5, fill=tk.X)
        ttk.Button(edit_frame, text="Redo", command=self.redo).pack(pady=5, fill=tk.X)
        ttk.Button(edit_frame, text="Grayscale", command=self.apply_grayscale).pack(pady=5, fill=tk.X)
        ttk.Button(edit_frame, text="Blur", command=self.apply_blur).pack(pady=5, fill=tk.X)
        ttk.Button(edit_frame, text="Rotate", command=self.rotate_image).pack(pady=5, fill=tk.X)

        # Group: Crop Tool
        crop_frame = ttk.Frame(self.sidebar)
        crop_frame.pack(pady=10, padx=10, fill=tk.X)
        ttk.Label(crop_frame, text="Crop Tool", anchor="w").pack(fill=tk.X, pady=5)
        self.crop_button = ttk.Button(crop_frame, text="Start Crop", command=self.start_crop, state=tk.DISABLED)
        self.crop_button.pack(pady=5, fill=tk.X)
        self.apply_crop_button = ttk.Button(crop_frame, text="Apply Crop", command=self.apply_crop, state=tk.DISABLED)
        self.apply_crop_button.pack(pady=5, fill=tk.X)

        # Group: Drawing Tools
        draw_frame = ttk.Frame(self.sidebar)
        draw_frame.pack(pady=10, padx=10, fill=tk.X)
        ttk.Label(draw_frame, text="Drawing Tools", anchor="w").pack(fill=tk.X, pady=5)
        self.brush_button = ttk.Button(draw_frame, text="Brush", command=self.select_brush, state=tk.DISABLED)
        self.brush_button.pack(pady=5, fill=tk.X)
        self.shapes_button = ttk.Button(draw_frame, text="Shapes", command=self.select_shape_tool, state=tk.DISABLED)
        self.shapes_button.pack(pady=5, fill=tk.X)
        self.color_button = ttk.Button(draw_frame, text="Color", command=self.select_color, state=tk.DISABLED)
        self.color_button.pack(pady=5, fill=tk.X)

        # Right side: Image Viewer
        self.viewer_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.viewer_frame, weight=3)

        self.canvas = tk.Canvas(self.viewer_frame, bg="#2e3440", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def update_buttons_state(self):
        """Enable or disable buttons based on the image state."""
        state = tk.NORMAL if self.image else tk.DISABLED
        self.brush_button.config(state=state)
        self.shapes_button.config(state=state)
        self.color_button.config(state=state)
        self.crop_button.config(state=state)

    def open_image(self):
        """Open an image and display it on the canvas."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.bmp;*.gif")])
        if file_path:
            self.file_path = file_path
            self.image = Image.open(file_path)
            self.history = [self.image.copy()]  # Reset history
            self.redo_stack = []  # Clear redo stack
            self.display_image()
            self.update_tool_states()  # Enable tools after loading an image
            self.update_buttons_state()

    def update_tool_states(self):
        """Enable or disable tools based on image presence."""
        state = tk.NORMAL if self.image else tk.DISABLED
        self.brush_button.config(state=state)
        self.shapes_button.config(state=state)
        self.color_button.config(state=state)

    def save_image(self):
        """Save the current edited image."""
        if self.image:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if save_path:
                self.image.save(save_path)
                self.unsaved_changes = False  # Cambios guardados
                messagebox.showinfo("Save Image", "Image saved successfully.")
        else:
            messagebox.showerror("Error", "No image is loaded.")

    def display_image(self):
        """Display the image on the canvas."""
        if self.image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            resized_image = self.image.copy()
            resized_image.thumbnail((canvas_width, canvas_height))
            self.photo = ImageTk.PhotoImage(resized_image)
            
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.photo, anchor=tk.CENTER)

            if self.crop_rectangle:
                self.canvas.delete(self.crop_rectangle)
                scale_x = canvas_width / self.image.width
                scale_y = canvas_height / self.image.height
                scaled_coords = [
                    self.start_x * scale_x, self.start_y * scale_y,
                    self.end_x * scale_x, self.end_y * scale_y
                ]
                self.crop_rectangle = self.canvas.create_rectangle(*scaled_coords, outline="#FF0000", width=2)

    def save_state(self):
        """Save the current image state in history."""
        if self.image:
            self.history.append(self.image.copy())
            if len(self.history) > 20:
                self.history.pop(0)
            self.redo_stack = []  # Clear redo stack
    
    def start_crop(self):
        if self.image:
            self.canvas.bind("<Button-1>", self.start_crop_rect)
            self.canvas.bind("<B1-Motion>", self.update_crop_rect)
            self.canvas.bind("<ButtonRelease-1>", self.finish_crop_rect)
            self.apply_crop_button.config(state=tk.DISABLED)
            messagebox.showinfo("Crop Mode", "Click and drag to select an area to crop.")

    def start_crop_rect(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.crop_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#FF0000", width=2
        )

    def update_crop_rect(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.canvas.coords(self.crop_rectangle, self.start_x, self.start_y, self.end_x, self.end_y)

    def finish_crop_rect(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.apply_crop_button.config(state=tk.NORMAL)

    def apply_crop(self):
        if not self.crop_rectangle:
            return

        canvas_bbox = self.canvas.coords(self.crop_rectangle)
        scale_x = self.image.width / self.canvas.winfo_width()
        scale_y = self.image.height / self.canvas.winfo_height()

        left = int(min(canvas_bbox[0], canvas_bbox[2]) * scale_x)
        top = int(min(canvas_bbox[1], canvas_bbox[3]) * scale_y)
        right = int(max(canvas_bbox[0], canvas_bbox[2]) * scale_x)
        bottom = int(max(canvas_bbox[1], canvas_bbox[3]) * scale_y)

        if left >= right or top >= bottom:
            messagebox.showerror("Invalid Crop", "The selected area is invalid.")
            return

        self.save_state()
        self.image = self.image.crop((left, top, right, bottom))
        self.display_image()

        # Limpiar herramientas de recorte
        self.canvas.delete(self.crop_rectangle)
        self.crop_rectangle = None
        self.apply_crop_button.config(state=tk.DISABLED)


    def undo(self):
        """Undo the last change on the image."""
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.image = self.history[-1].copy()
            self.display_image()
        else:
            messagebox.showinfo("Undo", "No more changes to undo.")

    def redo(self):
        """Redo the last undone change."""
        if self.redo_stack:
            self.image = self.redo_stack.pop()
            self.history.append(self.image.copy())
            self.display_image()
        else:
            messagebox.showinfo("Redo", "No more changes to redo.")

    def apply_grayscale(self):
        """Apply a grayscale filter to the image."""
        if self.image:
            self.save_state()
            self.image = self.image.convert("L").convert("RGB")
            self.display_image()

    def apply_blur(self):
        """Apply a blur filter to the image."""
        if self.image:
            self.save_state()
            self.image = self.image.filter(ImageFilter.BLUR)
            self.display_image()

    def rotate_image(self):
        """Rotate the image 90 degrees."""
        if self.image:
            self.save_state()
            self.image = self.image.rotate(90, expand=True)
            self.display_image()

    def start_drawing(self, event):
        """Start drawing on the canvas."""
        self.drawing = True
        self.draw_x = event.x
        self.draw_y = event.y

    def draw(self, event):
        """Draw on the canvas with selected brush size and color."""
        if self.drawing:
            self.canvas.create_line(self.draw_x, self.draw_y, event.x, event.y, width=self.brush_size, fill=self.brush_color, capstyle=tk.ROUND, smooth=True)
            self.draw_x = event.x
            self.draw_y = event.y
            self.save_state()

    def stop_drawing(self, event):
        """Stop drawing."""
        self.drawing = False

    def select_brush(self):
        """Select the brush tool to draw freely."""
        self.shape_tool = None

    def select_shape_tool(self):
        """Select a shape tool (circle, rectangle, arrow)."""
        self.shape_tool = "shape"

    def select_color(self):
        """Select a brush color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.brush_color = color

    def draw_shape(self, event):
        """Draw a selected shape (circle, rectangle, arrow)."""
        if self.shape_tool == "shape":
            if self.start_shape_x and self.start_shape_y:
                # Draw rectangle, circle, or arrow
                shape = self.shape_tool
                if shape == "circle":
                    self.canvas.create_oval(self.start_shape_x, self.start_shape_y, event.x, event.y, outline=self.brush_color, width=self.brush_size)
                elif shape == "rectangle":
                    self.canvas.create_rectangle(self.start_shape_x, self.start_shape_y, event.x, event.y, outline=self.brush_color, width=self.brush_size)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()
