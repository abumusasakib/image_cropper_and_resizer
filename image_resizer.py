import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import io
import threading

class ImageResizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer")

        self.image = None
        self.display_image = None
        self.scale_ratio = 1

        # Default values for image dimensions and file size limits
        self.default_width = 300
        self.default_height = 80
        self.default_min_size = 3 * 1024  # 3 KB
        self.default_max_size = 60 * 1024  # 60 KB

        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.open_button = tk.Button(root, text="Open Image", command=self.open_image)
        self.open_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(root, text="Save Resized Image", command=self.save_image)
        self.save_button.pack(side=tk.RIGHT)
        self.save_button.config(state=tk.DISABLED)

        # Loading label
        self.loading_label = tk.Label(root, text="", fg="red")
        self.loading_label.pack(side=tk.BOTTOM)

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

    def save_image(self):
        if self.image is None or not self.image.any():
            return

        # Ask for dimensions and file size limits
        width = simpledialog.askinteger("Input", "Enter the width of the resized image (-1 to keep original width):",
                                        initialvalue=self.default_width, minvalue=-1)
        height = simpledialog.askinteger("Input", "Enter the height of the resized image (-1 to keep original height):",
                                         initialvalue=self.default_height, minvalue=-1)
        min_file_size = simpledialog.askinteger("Input", "Enter the minimum file size (in KB):",
                                                initialvalue=self.default_min_size // 1024, minvalue=1) * 1024
        max_file_size = simpledialog.askinteger("Input", "Enter the maximum file size (in KB):",
                                                initialvalue=self.default_max_size // 1024, minvalue=1) * 1024

        # Start processing in a separate thread to avoid blocking the UI
        threading.Thread(target=self.process_image, args=(width, height, min_file_size, max_file_size)).start()

    def process_image(self, width, height, min_file_size, max_file_size):
        self.show_loading("Processing image...")

        # Use original dimensions if -1 is entered
        if width == -1:
            width = self.pil_image.width
        if height == -1:
            height = self.pil_image.height

        # Resize the image to the specified dimensions
        resized_image_pil = Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        resized_image_pil = resized_image_pil.resize((width, height))

        # Save the image ensuring it stays within the file size limits
        quality = 95
        success = False
        while True:
            with io.BytesIO() as buffer:
                resized_image_pil.save(buffer, format="JPEG", quality=quality)
                size = buffer.tell()
                if min_file_size <= size <= max_file_size or quality <= 10:
                    file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
                    if file_path:
                        resized_image_pil.save(file_path, format="JPEG", quality=quality)
                        messagebox.showinfo("Success", "Image resized and saved successfully.")
                        success = True
                    break
                quality = quality - 5 if size > max_file_size else quality + 5

        # Notify if saving failed
        if not success:
            messagebox.showerror("Error", "Failed to save the image within the specified size constraints.")
        
        self.show_loading("")  # Hide loading indication after completion

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizer(root)
    root.mainloop()
