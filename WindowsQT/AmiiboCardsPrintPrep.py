import os
import subprocess
from PIL import Image
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QFileDialog, QRadioButton,
                               QPushButton, QLabel, QProgressBar, QMessageBox, QWidget)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from io import BytesIO

# Constants
IMG_WIDTH_MM = 54.4
IMG_HEIGHT_MM = 85.5
MARGIN_MM = 10
PAGE_WIDTH_MM = 210
PAGE_HEIGHT_MM = 297
PREVIEW_SCALE = 0.15
# Adjustment Factors based on observed discrepancies
WIDTH_ADJUSTMENT = 5.44 / 5.285
HEIGHT_ADJUSTMENT = 8.55 / 8.295


class PDFGeneratorThread(QThread):
    progress_updated = Signal(float)
    pdf_created = Signal(str)

    def __init__(self, folder_path, horizontal):
        super().__init__()
        self.folder_path = folder_path
        self.horizontal = horizontal

    def run(self):
        output_path = os.path.join(self.folder_path, "output.pdf")

        # Conversion factors and dimensions
        conversion_factor = 300 / 25.4
        page_width_px = int(PAGE_WIDTH_MM * conversion_factor)
        page_height_px = int(PAGE_HEIGHT_MM * conversion_factor)
        img_width_px = int(IMG_WIDTH_MM * conversion_factor * WIDTH_ADJUSTMENT)
        img_height_px = int(IMG_HEIGHT_MM * conversion_factor * HEIGHT_ADJUSTMENT)
        margin_px = int(MARGIN_MM * conversion_factor)

        # Create blank canvas
        cmd = f'convert -size {page_width_px}x{page_height_px} xc:white "{output_path}"'
        subprocess.run(cmd, shell=True)

        # Loop through the images and place them on the canvas
        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                x = col * img_width_px + margin_px
                y = row * img_height_px + margin_px
                image_path = os.path.join(self.folder_path, f"image{idx + 1}.png")
                img = Image.open(image_path)
                if self.horizontal:
                    img = img.rotate(90, expand=True)
                img = img.resize((img_width_px, img_height_px))
                resized_path = f'resized{idx}.png'
                img.save(resized_path)
                cmd = f'composite -geometry +{x}+{y} "{resized_path}" "{output_path}" "{output_path}"'
                subprocess.run(cmd, shell=True)
                os.remove(resized_path)
                self.progress_updated.emit((idx + 1) / 9)

        self.pdf_created.emit(output_path)


class PDFGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create widgets and layout
        layout = QVBoxLayout()
        self.folder_button = QPushButton("Select Folder")
        self.vertical_button = QRadioButton("Vertical")
        self.horizontal_button = QRadioButton("Horizontal")
        self.preview_button = QPushButton("Preview")
        self.preview_label = QLabel()
        self.process_button = QPushButton("Generate PDF")
        self.loading_bar = QProgressBar()

        # Set default folder
        self.default_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "amiibo")
        if not os.path.exists(self.default_folder):
            os.makedirs(self.default_folder)

        self.folder_button.clicked.connect(self.select_folder)
        self.preview_button.clicked.connect(self.preview_images)
        self.process_button.clicked.connect(self.generate_pdf)
        self.vertical_button.setChecked(True)

        layout.addWidget(self.folder_button)
        layout.addWidget(self.vertical_button)
        layout.addWidget(self.horizontal_button)
        layout.addWidget(self.preview_button)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.process_button)
        layout.addWidget(self.loading_bar)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", self.default_folder)
        if folder_path:
            self.default_folder = folder_path

    def preview_images(self):
        self.update_preview(self.default_folder)

    def generate_pdf(self):
        self.loading_bar.setValue(0)
        self.thread = PDFGeneratorThread(self.default_folder, self.horizontal_button.isChecked())
        self.thread.progress_updated.connect(self.update_progress_bar)
        self.thread.pdf_created.connect(self.show_pdf_created_dialog)
        self.thread.start()

    def update_progress_bar(self, fraction):
        self.loading_bar.setValue(int(fraction * 100))

    def show_pdf_created_dialog(self, output_path):
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Information)
        dialog.setText("PDF Created")
        dialog.setInformativeText(f"PDF created as {output_path}")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec_()

    def update_preview(self, folder_path):
        conversion_factor = 300 / 25.4
        page_width_px = int(PAGE_WIDTH_MM * conversion_factor * PREVIEW_SCALE)
        page_height_px = int(PAGE_HEIGHT_MM * conversion_factor * PREVIEW_SCALE)
        preview_img = Image.new('RGB', (page_width_px, page_height_px), color='white')

        # Calculate space available for images
        available_width_mm = PAGE_WIDTH_MM - 2 * MARGIN_MM
        available_height_mm = PAGE_HEIGHT_MM - 2 * MARGIN_MM

        # Calculate image size based on available space
        img_width_mm = available_width_mm / 3
        img_height_mm = available_height_mm / 3

        # Loop through the images and place them on the canvas
        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                x = col * int(img_width_mm * conversion_factor * PREVIEW_SCALE * WIDTH_ADJUSTMENT) + int(MARGIN_MM * conversion_factor * PREVIEW_SCALE)
                y = row * int(img_height_mm * conversion_factor * PREVIEW_SCALE * HEIGHT_ADJUSTMENT) + int(MARGIN_MM * conversion_factor * PREVIEW_SCALE)
                image_path = os.path.join(folder_path, f"image{idx + 1}.png")
                img = Image.open(image_path)
                if self.horizontal_button.isChecked():
                    img = img.rotate(90, expand=True)
                img = img.resize((int(img_width_mm * conversion_factor * PREVIEW_SCALE * WIDTH_ADJUSTMENT),
                                  int(img_height_mm * conversion_factor * PREVIEW_SCALE * HEIGHT_ADJUSTMENT)))
                preview_img.paste(img, (x, y))

        # Convert the Image object to a QPixmap
        buf = BytesIO()
        preview_img.save(buf, format='png')
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())

        # Update the preview label
        self.preview_label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication()
    window = PDFGeneratorApp()
    window.show()
    app.exec_()
