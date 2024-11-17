from PIL import Image, ImageTk, ImageSequence
import tkinter as tk
from tkinter import messagebox

class ImageViewer:
    def __init__(self, app):
        self.app = app
        self.original_image = None
        self.is_gif = False
        self.gif_frames = None
        self.current_frame = 0
        self.photo = None
        self.zoom_factor = 1.0
        self.stop_animation = False
        self.images = []
        self.current_index = 0
        self.canvas_width = None
        self.canvas_height = None

    def update_canvas_size(self):
        """Update the canvas dimensions only when its size changes."""
        self.canvas_width = self.app.canvas.winfo_width()
        self.canvas_height = self.app.canvas.winfo_height()

    def load_image(self, image_path):
        """Load a static image or an optimized GIF."""
        try:
            # Try to load the image
            self.stop_animation = True
            self.app.root.update_idletasks()
            self.original_image = Image.open(image_path)
            
            # Verify if the image was loaded correctly
            if not self.original_image:
                raise ValueError("The image could not be loaded correctly.")
            
            # Determines if it is a GIF
            self.is_gif = image_path.lower().endswith('.gif')
            self.zoom_factor = 1.0
            self.update_canvas_size()

            if self.is_gif:
                try:
                    self.gif_frames = ImageSequence.Iterator(self.original_image)
                    self.current_frame = 0
                    self.stop_animation = False
                    self.animate_gif()
                except Exception as e:
                    raise ValueError(f"Error processing the GIF: {e}")
            else:
                self.display_image()

            self.app.update_info(image_path)

        except Exception as e:
            messagebox.showerror("Error", f"The image could not be opened: {e}")

    def animate_gif(self):
        """Animate the GIF efficiently and handle frame errors."""
        if self.stop_animation or not self.is_gif:
            return

        try:
            # Attempting to access the current framework
            self.original_image.seek(self.current_frame)
            frame = self.original_image.copy()

            # Validate if the frame is valid
            if frame is None:
                raise ValueError(f"The {self.current_frame} of the GIF is invalid.")

            # Resize the frame
            frame = frame.resize(
                (int(self.canvas_width * self.zoom_factor), int(self.canvas_height * self.zoom_factor)),
                Image.Resampling.LANCZOS
            )

            # Show frame
            self.photo = ImageTk.PhotoImage(frame)
            self.app.canvas.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.photo, anchor=tk.CENTER)

            # Configure the following table
            self.current_frame = (self.current_frame + 1) % getattr(self.original_image, "n_frames", 1)
            delay = self.original_image.info.get('duration', 100)
            self.app.root.after(delay, self.animate_gif)

        except EOFError:
            # End of GIF reached; restart
            self.current_frame = 0
            self.app.root.after(100, self.animate_gif)
        except Exception as e:
            # Handling other errors
            messagebox.showerror("Error", f"Error processing the GIF: {e}")
            self.stop_animation = True

    def display_image(self):
        if self.original_image:
            self.update_canvas_size()
            image = self.original_image.copy().resize(
                (int(self.canvas_width * self.zoom_factor), int(self.canvas_height * self.zoom_factor)),
                Image.Resampling.LANCZOS
            )
            self.photo = ImageTk.PhotoImage(image)
            self.app.canvas.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.photo, anchor=tk.CENTER)

    def zoom_in(self):
        self.zoom_factor *= 1.1
        if self.is_gif:
            self.animate_gif()
        else:
            self.display_image()

    def zoom_out(self):
        self.zoom_factor /= 1.1
        if self.is_gif:
            self.animate_gif()
        else:
            self.display_image()

    def stop_gif_animation(self):
        self.stop_animation = True

    def display_frame(self, frame):
        canvas_width = self.app.canvas.winfo_width()
        canvas_height = self.app.canvas.winfo_height()
        frame = frame.copy()
        frame.thumbnail((int(canvas_width * self.zoom_factor), int(canvas_height * self.zoom_factor)))
        self.photo = ImageTk.PhotoImage(frame)
        self.app.canvas.delete("all")
        self.app.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.photo, anchor=tk.CENTER)

    def display_image(self):
        if self.original_image:
            canvas_width = self.app.canvas.winfo_width()
            canvas_height = self.app.canvas.winfo_height()
            self.image = self.original_image.copy()
            self.image.thumbnail((int(canvas_width * self.zoom_factor), int(canvas_height * self.zoom_factor)))
            self.photo = ImageTk.PhotoImage(self.image)
            self.app.canvas.delete("all")
            self.app.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.photo, anchor=tk.CENTER)

    def rotate_image(self):
        if self.original_image:
            if self.is_gif:
                self.gif_frames = [frame.rotate(90, expand=True) for frame in self.gif_frames]
                self.display_frame(self.gif_frames[self.current_frame])
            else:
                self.original_image = self.original_image.rotate(90, expand=True)
                self.display_image()

    def zoom_in(self):
        self.zoom_factor *= 1.1
        if self.is_gif:
            self.display_frame(self.gif_frames[self.current_frame])
        else:
            self.display_image()

    def zoom_out(self):
        self.zoom_factor /= 1.1
        if self.is_gif:
            self.display_frame(self.gif_frames[self.current_frame])
        else:
            self.display_image()

    def load_images(self, images):
        self.images = images
        self.current_index = 0
        if self.images:
            self.load_image(self.images[self.current_index])
