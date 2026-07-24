# SigForge & Desktop Image Toolset

A comprehensive suite of image optimization tools featuring both a **Modern Web Application (SigForge)** that runs entirely in the browser and a **Python Desktop GUI Suite** for robust, local processing.

These tools are specifically designed to optimize signatures and photos for academic and registration portals (such as the Dhaka University dashboard), ensuring strict size constraints (e.g., 3 KB - 60 KB) and aspect ratios are satisfied without distortion or loss of quality.

---

## 🌐 Web Application: SigForge (`index.html`)

SigForge is a client-side web application built with HTML5 Canvas, Vanilla CSS, and modern animations. It can be opened locally in any browser or hosted instantly on **GitHub Pages**.

### Web Features

- **Signature Processor:** Centers signature images on a square `600x600` canvas with white padding. Includes interactive mouse panning and a zoom slider (`0.1x` to `3.0x`) to size down signatures (safeguarding against cropper clip-offs). Calculates and alerts you about final file size constraints in real-time.
- **Image Resizer:** Easily resize images to target dimensions. Supports aspect-ratio locking and automatic padding (white, transparent, or none) for letterboxing.
- **Custom Cropper:** Click and drag to draw a crop selection box over your loaded image to crop it instantly.
- **Batch Resizer:** Multi-file loader to batch resize lists of images to standard presets (e.g., `300x80` signature, `300x300` avatar).

---

## 🖥️ Desktop GUI Suite (Python)

For local operations, the project includes four dedicated Tkinter-based desktop applications.

### 1. Signature Processor (`process_sig.py`)

- **Drag & Drop:** Drop any image file directly onto the window.
- **Pan & Zoom Controls:** Interactive mouse dragging to pan the signature, plus a horizontal slider to scale the signature (`0.1x` to `3.0x`).
- **Standardized Canvas Output:** Automatically pastes the signature onto a `600x600` solid white background (with the signature scaled to fit within a `400x180` boundary box) to satisfy portal cropping boxes.
- **Size Validation:** Validates that the output file size falls within the requested `3 KB` to `60 KB` limits.

### 2. Image Resizer (`image_resizer.py`)

- **RGBA Transparency Preservation:** Preserves alpha channels and transparency when saving PNG files, with automatic transparent or white padding modes.
- **Dimensions Adjustment:** Custom width/height resizing with optional aspect ratio maintenance.
- **File Size Constraint Loop:** Iteratively compresses JPEG images to hit a target file size (enter `0` to bypass).

### 3. Image Cropper (`image_cropper.py`)

- **Draw to Crop:** Drag a rectangular crop boundary on the window.
- **Size Compression:** Compress cropped images to target constraints.

### 4. Batch Image Resizer (`batch_image_resizer.py`)

- **Recursive Scanning:** Scans folders recursively for files.
- **Similarity-Based Resizing:** Resizes only images within a configurable pixel tolerance of target presets.
- **Workflow Safety:** Displays a preview window detailing planned actions and skips before modification.

---

## 🛠️ Desktop Requirements & Setup

To run the Python desktop apps, ensure you have Python 3.7+ installed.

### Installation

Install dependencies via pip:

```bash
pip install -r requirements.txt
```

### Running the Desktop Apps

Launch any tool from your terminal:

```bash
python process_sig.py       # Signature Processor GUI
python image_resizer.py     # Image Resizer GUI
python image_cropper.py     # Image Cropper GUI
python batch_image_resizer.py # Batch Resizer GUI
```

---

## 🚀 Hosting on GitHub Pages

Because **SigForge (`index.html`)** runs entirely on client-side JavaScript:

1. Push this repository to GitHub.
2. Go to **Settings > Pages** in your GitHub repository.
3. Select the branch (e.g., `main`) and root folder (`/`), then click **Save**.
4. Your application will be live at: `https://abumusasakib.github.io/image_cropper_and_resizer/`
