import os
import subprocess
from PIL import Image
from PySide6.QtWidgets import (QApplication, QWidget, QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtUiTools import QUiLoader
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
        conversion_factor = 300 / 25.4
        page_width_px = int(PAGE_WIDTH_MM * conversion_factor)
        page_height_px = int(PAGE_HEIGHT_MM * conversion_factor)
        img_width_px = int(IMG_WIDTH_MM * conversion_factor * WIDTH_ADJUSTMENT)
        img_height_px = int(IMG_HEIGHT_MM * conversion_factor * HEIGHT_ADJUSTMENT)
        margin_px = int(MARGIN_MM * conversion_factor)

        cmd = f'convert -size {page_width_px}x{page_height_px} xc:white "{output_path}"'
        subprocess.run(cmd, shell=True)

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

class PDFGeneratorApp(QWidget):  # Change from QMainWindow to QWidget
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("PDFGeneratorUI.ui", self)
        self.setLayout(self.ui.verticalLayout)  # Set layout directly on the widget

        self.default_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "amiibo")
        if not os.path.exists(self.default_folder):
            os.makedirs(self.default_folder)

        self.ui.folder_button.clicked.connect(self.select_folder)
        self.ui.preview_button.clicked.connect(self.preview_images)
        self.ui.process_button.clicked.connect(self.generate_pdf)
        self.ui.vertical_button.setChecked(True)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", self.default_folder)
        if folder_path:
            self.default_folder = folder_path

    def preview_images(self):
        self.update_preview(self.default_folder)

    def generate_pdf(self):
        self.ui.loading_bar.setValue(0)
        self.thread = PDFGeneratorThread(self.default_folder, self.ui.horizontal_button.isChecked())
        self.thread.progress_updated.connect(self.update_progress_bar)
        self.thread.pdf_created.connect(self.show_pdf_created_dialog)
        self.thread.start()

    def update_progress_bar(self, fraction):
        self.ui.loading_bar.setValue(int(fraction * 100))

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

        img_width_px = int(IMG_WIDTH_MM * conversion_factor * PREVIEW_SCALE)
        img_height_px = int(IMG_HEIGHT_MM * conversion_factor * PREVIEW_SCALE)

        for row in range(3):
            for col in range(3):
                idx = row * 3 + col
                image_path = os.path.join(folder_path, f"image{idx + 1}.png")
                img = Image.open(image_path)
                if self.ui.horizontal_button.isChecked():
                    img = img.rotate(90, expand=True)
                x = col * img_width_px
                y = row * img_height_px
                img = img.resize((img_width_px, img_height_px))
                preview_img.paste(img, (x, y))

        preview_buffer = BytesIO()
        preview_img.save(preview_buffer, format="PNG")
        qt_image = QPixmap()
        qt_image.loadFromData(preview_buffer.getvalue())
        self.ui.preview_label.setPixmap(qt_image)

if __name__ == "__main__":
    app = QApplication([])
    window = PDFGeneratorApp()
    window.show()
    app.exec_()
