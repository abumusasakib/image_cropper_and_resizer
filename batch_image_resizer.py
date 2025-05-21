import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import os
import threading

STANDARD_DIMENSIONS = [
    (1320, 2868), (2868, 1320),
    (1290, 2796), (2796, 1290),
    (1242, 2688), (2688, 1242),
    (1284, 2778), (2778, 1284),
]

DIMENSION_TOLERANCE = 100  # pixels

class ImageBatchResizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Resizer")

        self.label = tk.Label(root, text="Select a folder to resize images recursively.")
        self.label.pack()

        self.select_button = tk.Button(root, text="Select Folder", command=self.select_folder)
        self.select_button.pack(pady=10)

        self.loading_label = tk.Label(root, text="", fg="blue")
        self.loading_label.pack()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            threading.Thread(target=self.preview_folder, args=(folder_path,)).start()

    def show_loading(self, message):
        self.loading_label.config(text=message)
        self.root.update_idletasks()

    def is_close_to_standard(self, width, height):
        for std_w, std_h in STANDARD_DIMENSIONS:
            if abs(width - std_w) <= DIMENSION_TOLERANCE and abs(height - std_h) <= DIMENSION_TOLERANCE:
                return (std_w, std_h)
        return None

    def preview_folder(self, folder_path):
        self.show_loading("Scanning images...")

        to_resize = []
        to_skip = []

        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    try:
                        with Image.open(file_path) as img:
                            target_size = self.is_close_to_standard(*img.size)
                            if target_size:
                                to_resize.append((file_path, img.size, target_size))
                            else:
                                to_skip.append((file_path, img.size))
                    except Exception as e:
                        to_skip.append((file_path, f"Unreadable: {str(e)}"))
                else:
                    to_skip.append((file_path, "Not an image"))

        self.show_loading("")
        self.show_preview_dialog(folder_path, to_resize, to_skip)

    def show_preview_dialog(self, folder_path, to_resize, to_skip):
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Preview Resize Actions")
        preview_win.geometry("800x500")

        text_area = scrolledtext.ScrolledText(preview_win, wrap=tk.WORD)
        text_area.pack(expand=True, fill=tk.BOTH)

        text_area.insert(tk.END, f"Images to be resized ({len(to_resize)}):\n")
        for path, original_size, new_size in to_resize:
            text_area.insert(tk.END, f"- {path} ({original_size} → {new_size})\n")

        text_area.insert(tk.END, f"\nImages to be skipped ({len(to_skip)}):\n")
        for item in to_skip:
            path, reason = item
            text_area.insert(tk.END, f"- {path} (Reason: {reason})\n")

        text_area.config(state=tk.DISABLED)

        def on_confirm():
            preview_win.destroy()
            threading.Thread(target=self.process_folder, args=(to_resize,)).start()

        def on_cancel():
            preview_win.destroy()
            self.show_loading("Operation cancelled.")

        confirm_button = tk.Button(preview_win, text="Proceed", command=on_confirm, bg="green", fg="white")
        confirm_button.pack(side=tk.LEFT, padx=10, pady=5)

        cancel_button = tk.Button(preview_win, text="Cancel", command=on_cancel, bg="red", fg="white")
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=5)

    def process_folder(self, resize_list):
        self.show_loading("Processing and saving resized images...")

        processed_count = 0
        errors = []

        for file_path, _, target_size in resize_list:
            try:
                with Image.open(file_path) as img:
                    resized = img.resize(target_size, Image.LANCZOS)
                    resized.save(file_path)
                    processed_count += 1
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")

        self.show_loading("")

        result_msg = f"✅ Resizing completed.\n\nImages resized: {processed_count}\nErrors: {len(errors)}"
        if errors:
            error_summary = "\n".join(errors[:10])
            messagebox.showerror("Completed with Errors", f"{result_msg}\n\nTop Errors:\n{error_summary}")
        else:
            messagebox.showinfo("Success", result_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBatchResizer(root)
    root.mainloop()
