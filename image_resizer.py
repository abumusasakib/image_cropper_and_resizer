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

class ImageResizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer")
        self.root.geometry("500x400")

        self.image = None
        self.display_image = None
        self.scale_ratio = 1

        # Default values for image dimensions and file size limits
        self.default_width = 300
        self.default_height = 80
        self.default_min_size = 3 * 1024  # 3 KB
        self.default_max_size = 60 * 1024  # 60 KB

        # Bottom Frame for Buttons and Loading Label (packed first to preserve visibility)
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.open_button = tk.Button(self.button_frame, text="Open Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(self.button_frame, text="Save Resized Image", command=self.save_image)
        self.save_button.pack(side=tk.RIGHT, padx=10)
        self.save_button.config(state=tk.DISABLED)

        self.loading_label = tk.Label(self.button_frame, text="", fg="red")
        self.loading_label.pack(side=tk.BOTTOM)

        # Canvas (packed last, fills remaining space)
        self.canvas = tk.Canvas(root, bg="#f0f0f0")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_configure)

        # Enable Drag and Drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop)

    def show_loading(self, text=""):
        self.loading_label.config(text=text)
        self.root.update_idletasks()

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        try:
            self.image = Image.open(file_path)
        except Exception as e:
            print(f"Error: Could not open image. {e}")
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
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image. {e}")
            return

        self.show_image()

    def on_configure(self, event):
        if self.image is None:
            self.draw_placeholder()
        else:
            self.show_image()

    def draw_placeholder(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        # Draw a nice dashed rectangle/border and text
        self.canvas.create_rectangle(20, 20, w - 20, h - 20, outline="#cccccc", dash=(5, 5), width=2)
        self.canvas.create_text(w // 2, h // 2, text="Drag & Drop Image Here\nor\nClick 'Open Image' below",
                                justify=tk.CENTER, font=("Arial", 12, "italic"), fill="#888888")

    def show_image(self):
        self.pil_image = self.image.convert("RGB")

        # Resize image to fit canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        self.scale_ratio = min(self.canvas_width / self.pil_image.width, self.canvas_height / self.pil_image.height)
        new_width = int(self.pil_image.width * self.scale_ratio)
        new_height = int(self.pil_image.height * self.scale_ratio)
        self.display_image = self.pil_image.resize((new_width, new_height))
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.save_button.config(state=tk.NORMAL)

    def save_image(self):
        if self.image is None:
            return

        # Ask for dimensions and file size limits
        width = simpledialog.askinteger("Input", "Enter the width of the resized image (-1 to keep original width):",
                                        initialvalue=self.default_width, minvalue=-1)
        if width is None:
            return

        height = simpledialog.askinteger("Input", "Enter the height of the resized image (-1 to keep original height):",
                                         initialvalue=self.default_height, minvalue=-1)
        if height is None:
            return

        apply_padding = False
        if width != -1 and height != -1:
            apply_padding = messagebox.askyesno("Padding", "Would you like to add white padding (letterbox/pillarbox) to fit the image to the exact dimensions while preserving aspect ratio?")

        min_file_size = simpledialog.askinteger("Input", "Enter the minimum file size (in KB, 0 for no limit):",
                                                initialvalue=self.default_min_size // 1024, minvalue=0)
        if min_file_size is None:
            return
        min_file_size *= 1024

        max_file_size = simpledialog.askinteger("Input", "Enter the maximum file size (in KB, 0 for no limit):",
                                                initialvalue=self.default_max_size // 1024, minvalue=0)
        if max_file_size is None:
            return
        max_file_size *= 1024

        # Start processing in a separate thread to avoid blocking the UI
        threading.Thread(target=self.process_image, args=(width, height, min_file_size, max_file_size, apply_padding)).start()

    def process_image(self, width, height, min_file_size, max_file_size, apply_padding):
        self.show_loading("Processing image...")

        orig_w = self.pil_image.width
        orig_h = self.pil_image.height

        # Calculate width and height keeping original aspect ratio, and apply padding if both are specified and requested
        if width == -1 and height == -1:
            target_w = orig_w
            target_h = orig_h
            resized_image_pil = self.pil_image.resize((target_w, target_h))
        elif width == -1:
            target_h = height
            target_w = int(height * (orig_w / orig_h))
            resized_image_pil = self.pil_image.resize((target_w, target_h))
        elif height == -1:
            target_w = width
            target_h = int(width * (orig_h / orig_w))
            resized_image_pil = self.pil_image.resize((target_w, target_h))
        else:
            # Both specified: scale to fit
            scale = min(width / orig_w, height / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            fit_img = self.pil_image.resize((new_w, new_h))
            
            if apply_padding:
                # Create a new white background image of the exact target size
                resized_image_pil = Image.new("RGB", (width, height), (255, 255, 255))
                # Center the fit image onto the background
                paste_x = (width - new_w) // 2
                paste_y = (height - new_h) // 2
                resized_image_pil.paste(fit_img, (paste_x, paste_y))
            else:
                resized_image_pil = fit_img
                # Update width/height to the actual resized dimensions for status message
                width, height = new_w, new_h

        # Save the image ensuring it stays within the file size limits
        quality = 95
        success = False
        file_path = None

        if min_file_size == 0 and max_file_size == 0:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                resized_image_pil.save(file_path, format="JPEG", quality=quality)
                messagebox.showinfo("Success", f"Image resized to {width}x{height} and saved successfully.")
                success = True
        else:
            while True:
                with io.BytesIO() as buffer:
                    resized_image_pil.save(buffer, format="JPEG", quality=quality)
                    size = buffer.tell()
                    if min_file_size <= size <= max_file_size or quality <= 10:
                        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
                        if file_path:
                            resized_image_pil.save(file_path, format="JPEG", quality=quality)
                            messagebox.showinfo("Success", f"Image resized to {width}x{height} and saved successfully.")
                            success = True
                        break
                    quality = quality - 5 if size > max_file_size else quality + 5

        # Notify if saving failed
        if not success:
            messagebox.showerror("Error", "Failed to save the image within the specified size constraints.")
        else:
            # Open the containing folder after successful save
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
    app = ImageResizer(root)
    root.mainloop()
