import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import io
import numpy as np
import threading

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")

        self.image = None
        self.crop_rect = None
        self.rect_id = None
        self.start_x = None
        self.start_y = None
        self.display_image = None
        self.scale_ratio = 1

        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.open_button = tk.Button(root, text="Open Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(root, text="Save Crop", command=self.save_crop)
        self.save_button.pack(side=tk.RIGHT)
        self.save_button.config(state=tk.DISABLED)

        # Loading label
        self.loading_label = tk.Label(root, text="", fg="red")
        self.loading_label.pack(side=tk.BOTTOM)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def show_loading(self, text=""):
        self.loading_label.config(text=text)
        self.root.update_idletasks()

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.image = cv2.imread(file_path)
        if self.image is None:
            print("Error: Could not open image.")
            return

        self.show_image()

    def show_image(self):
        self.crop_rect = None
        self.rect_id = None
        self.start_x = None
        self.start_y = None

        self.cv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(self.cv_image)

        # Resize image to fit canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        self.scale_ratio = min(self.canvas_width / self.pil_image.width, self.canvas_height / self.pil_image.height)
        new_width = int(self.pil_image.width * self.scale_ratio)
        new_height = int(self.pil_image.height * self.scale_ratio)
        self.display_image = self.pil_image.resize((new_width, new_height))
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.save_button.config(state=tk.NORMAL)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.crop_rect = None

        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    def on_mouse_drag(self, event):
        if self.start_x and self.start_y:
            x1, y1 = self.start_x, self.start_y
            x2 = event.x
            y2 = event.y

            # Ensure the selection is a square
            side_length = min(abs(x2 - x1), abs(y2 - y1))
            if x2 < x1:
                x2 = x1 - side_length
            else:
                x2 = x1 + side_length

            if y2 < y1:
                y2 = y1 - side_length
            else:
                y2 = y1 + side_length

            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline='red')

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

        # Ensure the selection is a square
        side_length = min(abs(self.end_x - self.start_x), abs(self.end_y - self.start_y))
        if self.end_x < self.start_x:
            self.end_x = self.start_x - side_length
        else:
            self.end_x = self.start_x + side_length

        if self.end_y < self.start_y:
            self.end_y = self.start_y - side_length
        else:
            self.end_y = self.start_y + side_length

        self.crop_rect = (self.start_x, self.start_y, self.end_x, self.end_y)

    def save_crop(self):
        if not self.crop_rect or self.image is None or not self.image.any():
            return

        # Prompt for resize and max file size in the main thread
        resize = messagebox.askyesno("Resize", "Do you want to resize the cropped image?")
        max_file_size_kb = simpledialog.askinteger("Max File Size", "Enter the max file size (KB):", initialvalue=100, minvalue=1)
        if max_file_size_kb is None:  # User canceled input
            return

        # Start saving process in a separate thread
        threading.Thread(target=self.process_crop, args=(resize, max_file_size_kb)).start()

    def process_crop(self, resize, max_file_size_kb):
        self.show_loading("Processing crop...")

        # Calculate the crop coordinates on the original image
        x1, y1, x2, y2 = self.crop_rect
        x1 = int(x1 / self.scale_ratio)
        y1 = int(y1 / self.scale_ratio)
        x2 = int(x2 / self.scale_ratio)
        y2 = int(y2 / self.scale_ratio)

        cropped_image = self.image[y1:y2, x1:x2]

        if resize:
            width = simpledialog.askinteger("Width", "Enter the width:", initialvalue=300, minvalue=1)
            height = simpledialog.askinteger("Height", "Enter the height:", initialvalue=300, minvalue=1)
            if width and height:
                cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)).resize((width, height))
            else:
                return
        else:
            cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))

        max_file_size = max_file_size_kb * 1024  # Convert to bytes
        quality = 95
        success = False
        while True:
            with io.BytesIO() as buffer:
                cropped_image_pil.save(buffer, format="JPEG", quality=quality)
                size = buffer.tell()
                if size <= max_file_size or quality <= 10:
                    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
                    if file_path:
                        cropped_image_pil.save(file_path, format="JPEG", quality=quality)
                        messagebox.showinfo("Success", "Image cropped and saved successfully.")
                        success = True
                    break
                quality -= 5

        if not success:
            messagebox.showerror("Error", "Failed to save the image within the specified size constraints.")

        self.show_loading("")  # Hide loading indication after completion

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
