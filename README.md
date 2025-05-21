# Image Cropper, Resizer, and Batch Resizer

This project provides three main tools — **ImageCropper**, **ImageResizer**, and **ImageBatchResizer** — for interactive and automated image manipulation using Tkinter and OpenCV. With these tools, you can:

- Open and crop images interactively.
- Resize individual images.
- Recursively batch resize images within folders, based on dimension similarity.
- Compress images to meet file size constraints.

## Features

### Image Cropper

- **Open Images:** Load images from your file system.
- **Crop Area Selection:** Click and drag to define a square cropping area on the image.
- **Optional Resizing:** Resize cropped images to user-specified dimensions.
- **File Size Compression:** Save the cropped image as a JPEG with adjustable compression to meet a maximum file size constraint.

### Image Resizer

- **Resize and Save Images:** Resize an entire image to desired dimensions.
- **Batch Resizing (Optional):** Can be extended to support batch image resizing if desired.
- **Preserve Aspect Ratio (Optional):** Choose to maintain the original aspect ratio while resizing.

### Image Batch Resizer (NEW)

- **Recursive Folder Scanning:** Traverse all subdirectories to find supported images (`.jpg`, `.jpeg`, `.png`).
- **Resize Based on Similarity:** Only resize images that are within a configurable pixel tolerance of a set of standard resolutions (e.g., iPhone screen sizes).
- **Preview Before Action:** Lists which images will be resized and which will be skipped, along with reasons (e.g., size too different, unreadable, not an image).
- **User Confirmation:** Allows users to review and confirm the batch operation before resizing begins.
- **Overwrite In-Place:** Resizes and saves images directly, replacing originals (backup before use if needed).
- **Robust Error Handling:** Gracefully skips unreadable or unsupported files.

## Requirements

- **Python 3.7+**
- **Packages:**
  - `Pillow` (PIL)
  - `opencv-python`
  - `tkinter` (usually included with Python installations)

Install required packages:

```bash
pip install pillow opencv-python
````

## Setup

1. Clone or download this repository.
2. Ensure all required packages are installed.
3. Run any of the following tools based on your need:

   ```bash
   python image_cropper.py      # For cropping
   python image_resizer.py      # For individual resizing
   python image_batch_resizer.py  # For batch resizing
   ```

## Usage

### ImageCropper

1. **Run the Tool:**

   ```bash
   python image_cropper.py
   ```

2. **Open an Image:**

   - Click "Open Image" to load an image from your file system.

3. **Select Crop Area:**

   - Click and drag to select a square crop area.

4. **Save the Crop:**

   - Choose to resize and compress the cropped image if desired.
   - Set max file size (in KB) for compression.

### ImageResizer

1. **Run the Tool:**

   ```bash
   python image_resizer.py
   ```

2. **Resize Image:**

   - Open an image.
   - Resize to custom dimensions.
   - Optionally set max file size.
   - Save the result.

### ImageBatchResizer

1. **Run the Tool:**

   ```bash
   python image_batch_resizer.py
   ```

2. **Select Folder:**

   - Choose a root folder containing images.

3. **Preview Actions:**

   - A preview window will show:

     - Images to be resized (with original → new size)
     - Images to be skipped (with reasons)

4. **Confirm or Cancel:**

   - Click "Proceed" to start resizing or "Cancel" to abort.

5. **Processing:**

   - Images close to standard resolutions will be resized and saved in place.

## Notes

- **Thread Safety:** All tools use threading to ensure the UI remains responsive during long operations.
- **Error Handling:** Handles unreadable files, non-image inputs, and missing paths with user-friendly feedback.
- **Max File Size Constraint:** JPEG images are compressed iteratively to meet the desired size while maintaining acceptable quality.
- **Preview-first Workflow:** The batch resizer is especially careful — no changes are made until you explicitly approve them.

---

Feel free to contribute improvements, request features, or report bugs via issues.
