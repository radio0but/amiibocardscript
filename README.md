# PDF Generator for Animal Crossing

A script to generate a PDF from images, tailored to work with Animal Crossing. This guide will help you install and use the script on different operating systems.

## Installation Guide

### Requirements:
- Python 3.x
- PIL (Pillow)
- GdkPixbuf
- ImageMagick
- GTK+3

### Windows:
1. **Install Python 3.x**: Download the latest version from [Python's official website](https://www.python.org/downloads/).
2. **Install GTK+3**: Follow the instructions on the [GTK download page](https://www.gtk.org/docs/installations/windows/).
3. **Install ImageMagick**: Download and install from [ImageMagick's website](https://imagemagick.org/script/download.php#windows).
4. **Install Python Dependencies**: Open Command Prompt and run:
    ```bash
    pip install Pillow
    pip install PyGObject
    ```

### macOS:
1. **Install Python 3.x**: Download the latest version from [Python's official website](https://www.python.org/downloads/).
2. **Install GTK+3**: Use [Homebrew](https://brew.sh/):
    ```bash
    brew install gtk+3
    ```
3. **Install ImageMagick**: Use Homebrew:
    ```bash
    brew install imagemagick
    ```
4. **Install Python Dependencies**: Open Terminal and run:
    ```bash
    pip3 install Pillow
    pip3 install PyGObject
    ```

### Linux (Ubuntu/Debian):
1. **Install Python 3.x**: Python 3 is likely pre-installed. You can check the version by running `python3 --version`.
2. **Install GTK+3, ImageMagick, and GdkPixbuf**: Open Terminal and run:
    ```bash
    sudo apt-get install python3-gi gir1.2-gtk-3.0 imagemagick
    ```
3. **Install Python Dependencies**: Run:
    ```bash
    pip3 install Pillow
    ```

## Usage Guide:
1. **Run the Script**: Navigate to the directory where the script is located and run:
   - **Windows**: `python pdfgtkg.py`
   - **macOS/Linux**: `python3 pdfgtkg.py`
2. **Select a Folder**: Click the folder button and select the directory containing the images.
3. **Select Image Orientation**: Choose the desired orientation for the images (Vertical or Horizontal).
4. **Preview the Images**: Click the "Preview" button to see a preview of the PDF layout.
5. **Generate PDF**: Click the "Generate PDF" button. The PDF will be created in the selected folder.

## Notes:
- Make sure the images are named as "image1.png", "image2.png", etc., and are placed in the selected folder.

## License:
- Add license information if applicable.
