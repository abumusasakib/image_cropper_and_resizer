import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import io
import threading
import re
import os
import sys
import subprocess

class SignatureProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Signature Processor")
        self.root.geometry("500x520")

        self.image = None
        self.display_image = None
        
        # Pan and Zoom state variables
        self.pan_x = 0
        self.pan_y = 0
        self.zoom_factor = 1.0
        self.start_x = 0
        self.start_y = 0

        # Dhaka University signature requirements
        self.canvas_size = 600
        self.max_sig_width = 400
        self.max_sig_height = 180
        self.min_file_size = 3 * 1024  # 3 KB
        self.max_file_size = 60 * 1024  # 60 KB

        # Bottom Frame for Buttons and Loading Label (packed first to preserve visibility)
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.open_button = tk.Button(self.button_frame, text="Open Signature Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(self.button_frame, text="Save Processed Signature", command=self.save_image)
        self.save_button.pack(side=tk.RIGHT, padx=10)
        self.save_button.config(state=tk.DISABLED)

        self.loading_label = tk.Label(self.button_frame, text="", fg="red")
        self.loading_label.pack(side=tk.BOTTOM)

        # Zoom & Reset Controls Frame
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)

        self.zoom_label = tk.Label(self.control_frame, text="Zoom: 1.00x", font=("Arial", 10))
        self.zoom_label.pack(side=tk.LEFT)

        self.zoom_slider = tk.Scale(
            self.control_frame, 
            from_=0.1, 
            to=3.0, 
            resolution=0.05, 
            orient=tk.HORIZONTAL, 
            showvalue=False, 
            command=self.on_zoom_change
        )
        self.zoom_slider.set(1.0)
        self.zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.reset_button = tk.Button(self.control_frame, text="Reset View", command=self.reset_view)
        self.reset_button.pack(side=tk.RIGHT)

        # Canvas Frame (centered fixed 300x300 area representing the 600x600 canvas)
        self.canvas_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(pady=15)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=300, height=300, bg="#ffffff", cursor="fleur")
        self.canvas.pack()
        self.canvas.bind("<Configure>", self.on_configure)

        # Bind mouse events for panning
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)

        # Enable Drag and Drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop)

    def show_loading(self, text=""):
        self.loading_label.config(text=text)
        self.root.update_idletasks()

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not file_path:
            return
        try:
            self.image = Image.open(file_path)
            self.reset_view()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open signature image. {e}")
            return

        self.show_image()

    def drop(self, event):
        file_path = event.data
        if not file_path:
            return
        
        # Clean file path (TkinterDnD formatting)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        elif '{' in file_path:
            matches = re.findall(r'\{(.*?)\}', file_path)
            if matches:
                file_path = matches[0]
            else:
                file_path = file_path.split()[0]
        
        try:
            self.image = Image.open(file_path)
            self.reset_view()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open signature image. {e}")
            return

        self.show_image()

    def on_configure(self, event):
        if self.image is None:
            self.draw_placeholder()
        else:
            self.show_image()

    def draw_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(10, 10, 290, 290, outline="#cccccc", dash=(5, 5), width=2)
        self.canvas.create_text(150, 150, text="Drag & Drop Signature Here\nor\nClick 'Open Signature Image'",
                                justify=tk.CENTER, font=("Arial", 10, "italic"), fill="#888888")

    def on_drag_start(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag_motion(self, event):
        if self.image is None:
            return
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.pan_x += dx
        self.pan_y += dy
        self.start_x = event.x
        self.start_y = event.y
        self.show_image()

    def on_zoom_change(self, value):
        self.zoom_factor = float(value)
        self.zoom_label.config(text=f"Zoom: {self.zoom_factor:.2f}x")
        if self.image is not None:
            self.show_image()

    def reset_view(self):
        self.pan_x = 0
        self.pan_y = 0
        self.zoom_factor = 1.0
        self.zoom_slider.set(1.0)
        self.zoom_label.config(text="Zoom: 1.00x")
        if self.image is not None:
            self.show_image()

    def show_image(self):
        if self.image.mode in ('RGBA', 'LA') or (self.image.mode == 'P' and 'transparency' in self.image.info):
            self.pil_image = self.image.convert("RGBA")
        else:
            self.pil_image = self.image.convert("RGB")

        orig_w = self.pil_image.width
        orig_h = self.pil_image.height

        # Base scale to fit within 200x90 area (which is 400x180 target size scaled down 2x for preview)
        base_scale = min(200 / orig_w, 90 / orig_h)
        display_scale = base_scale * self.zoom_factor

        new_width = max(1, int(orig_w * display_scale))
        new_height = max(1, int(orig_h * display_scale))

        self.display_image = self.pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Render onto a 300x300 white background to simulate the preview
        preview_bg = Image.new("RGB", (300, 300), (255, 255, 255))
        
        paste_x = (300 - new_width) // 2 + self.pan_x
        paste_y = (300 - new_height) // 2 + self.pan_y

        if self.pil_image.mode == "RGBA":
            preview_bg.paste(self.display_image, (paste_x, paste_y), self.display_image)
        else:
            preview_bg.paste(self.display_image, (paste_x, paste_y))

        self.tk_image = ImageTk.PhotoImage(preview_bg)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        # Draw a thin border representing the boundaries of the canvas
        self.canvas.create_rectangle(0, 0, 299, 299, outline="#dddddd")
        self.save_button.config(state=tk.NORMAL)

    def save_image(self):
        if self.image is None:
            return

        # Prompt user to choose save path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")],
            initialfile="signature_processed.png"
        )
        if not file_path:
            return

        # Start processing in a separate thread to avoid blocking the UI
        threading.Thread(target=self.process_image, args=(file_path,)).start()

    def process_image(self, file_path):
        self.show_loading("Processing signature...")

        orig_w = self.pil_image.width
        orig_h = self.pil_image.height

        # Scale signature to fit comfortably in the center of the 600x600 canvas
        base_scale = min(self.max_sig_width / orig_w, self.max_sig_height / orig_h)
        scale = base_scale * self.zoom_factor
        
        new_w = max(1, int(orig_w * scale))
        new_h = max(1, int(orig_h * scale))
        fit_img = self.pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Create solid white background (600x600)
        padded_img = Image.new("RGB", (self.canvas_size, self.canvas_size), (255, 255, 255))

        # Center and apply pan offsets (pan offsets on screen are doubled for 600x600 canvas)
        paste_x = (self.canvas_size - new_w) // 2 + int(self.pan_x * 2)
        paste_y = (self.canvas_size - new_h) // 2 + int(self.pan_y * 2)

        # Use transparency mask if original has alpha channel
        if self.pil_image.mode == "RGBA":
            padded_img.paste(fit_img, (paste_x, paste_y), fit_img)
        else:
            padded_img.paste(fit_img, (paste_x, paste_y))

        save_format = "PNG" if file_path.lower().endswith(".png") else "JPEG"

        success = False
        try:
            # Save the processed image
            padded_img.save(file_path, format=save_format, optimize=True)
            success = True
            
            # Check the final file size
            size = os.path.getsize(file_path)
            size_kb = size / 1024
            
            if self.min_file_size <= size <= self.max_file_size:
                messagebox.showinfo(
                    "Success", 
                    f"Signature processed and saved successfully!\n\n"
                    f"Canvas size: {self.canvas_size}x{self.canvas_size}\n"
                    f"File size: {size_kb:.2f} KB (Within the 3 KB - 60 KB limit)."
                )
            else:
                messagebox.showwarning(
                    "Size Constraint Warning",
                    f"Signature saved, but the file size is {size_kb:.2f} KB.\n\n"
                    f"This is outside the requirements of 3 KB - 60 KB.\n"
                    f"Try scaling or saving in a different format."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save the processed signature. {e}")

        # Open the containing folder after successful save
        if success:
            try:
                folder_path = os.path.dirname(file_path)
                if os.name == 'nt':
                    os.startfile(folder_path)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', folder_path])
                else:
                    subprocess.Popen(['xdg-open', folder_path])
            except Exception as e:
                print(f"Error opening folder: {e}")
        
        self.show_loading("")  # Hide loading indication after completion

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SignatureProcessor(root)
    root.mainloop()
