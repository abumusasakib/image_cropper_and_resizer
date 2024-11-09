# Image Cropper and Resizer

This project provides two main tools, **ImageCropper** and **ImageResizer**, for interactive image manipulation using Tkinter and OpenCV. With these tools, you can:

- Open images.
- Select and crop regions with flexible or square constraints.
- Optionally resize the cropped image.
- Compress the image to a specified maximum file size.

## Features

### Image Cropper

- **Open Images:** Load images from your file system.
- **Crop Area Selection:** Click and drag to define a square cropping area on the image.
- **Optional Resizing:** Resize cropped images to user-specified dimensions.
- **File Size Compression:** Save the cropped image as a JPEG with adjustable compression to meet a maximum file size constraint.

### Image Resizer

- **Resize and Save Images:** Resize an entire image to desired dimensions.
- **Batch Resizing (Optional):** This can be extended to support batch image resizing if desired.
- **Preserve Aspect Ratio (Optional):** Choose to maintain the original aspect ratio while resizing.

## Requirements

- **Python 3.7+**
- **Packages:**
  - `Pillow` (PIL)
  - `opencv-python`
  - `tkinter` (usually included with Python installations)

To install `Pillow` and `opencv-python`:

```bash
pip install pillow opencv-python
```

## Setup

1. Clone or download this repository.
2. Ensure all required packages are installed.
3. Run `image_cropper.py` to start the cropping tool.
4. Run `image_resizer.py` to start the resizing tool.

## Usage

### ImageCropper

1. **Run the Tool:**

   ```bash
   python image_cropper.py
   ```

2. **Open an Image:**
   - Click on "Open Image" to load an image from your file system.
3. **Select a Crop Area:**
   - Click and drag on the image to select a square region to crop. A red square will indicate the selected area.
4. **Save the Crop:**
   - Click "Save Crop."
   - A prompt will ask if you want to resize the cropped area. If "Yes," you can enter width and height.
   - You will also be prompted to enter a maximum file size in KB for compression.
5. **File Saving:**
   - After setting options, select the destination to save the cropped image. The image will be compressed if needed to meet the specified file size.

### ImageResizer

1. **Run the Tool:**

   ```bash
   python image_resizer.py
   ```

2. **Resize Image:**
   - Open the image.
   - Draw the rectangle around the image and file size limits.
   - Save the resized image to a specified location.

## Notes

- **Thread Safety:** The `ImageCropper` and `ImageResizer` class uses threading to handle image processing tasks asynchronously, ensuring the UI remains responsive.
- **Error Handling:** The tool manages missing file paths, incorrect image formats, and unexpected user inputs with helpful error messages.
- **Max File Size Constraint:** Compression quality is reduced iteratively to meet the specified file size while balancing quality.
