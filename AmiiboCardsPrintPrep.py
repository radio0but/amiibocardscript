import gi
import os
import subprocess
from PIL import Image
from io import BytesIO
from gi.repository import GLib
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

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

# Load Glade file
builder = Gtk.Builder()
builder.add_from_file("pdf_generator.glade")


class PDFGeneratorApp:
    def __init__(self):
        # Get objects from Glade file
        self.window = builder.get_object("window1")
        self.folder_button = builder.get_object("folder_button")
        self.vertical_button = builder.get_object("vertical_button")
        self.horizontal_button = builder.get_object("horizontal_button")
        self.preview_button = builder.get_object("preview_button")
        self.preview_image = builder.get_object("preview_image")
        self.process_button = builder.get_object("process_button")
        self.loading_bar = builder.get_object("loading_bar")

        # Set default folder
        self.default_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "amiibo")
        if not os.path.exists(self.default_folder):
            os.makedirs(self.default_folder)
        self.folder_button.set_current_folder(self.default_folder)

        # Connect signals
        self.preview_button.connect("clicked", self.preview_images)
        self.process_button.connect("clicked", self.generate_pdf_thread)

        # Show window
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

    def update_progress_bar(self, fraction):
        self.loading_bar.set_fraction(fraction)

    def generate_pdf(self):
        folder_path = self.folder_button.get_filename() or self.default_folder
        output_path = os.path.join(folder_path, "output.pdf")

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
                image_path = os.path.join(folder_path, f"image{idx + 1}.png")
                img = Image.open(image_path)
                if self.horizontal_button.get_active():
                    img = img.rotate(90, expand=True)
                img = img.resize((img_width_px, img_height_px))
                resized_path = f'resized{idx}.png'
                img.save(resized_path)
                cmd = f'composite -geometry +{x}+{y} "{resized_path}" "{output_path}" "{output_path}"'
                subprocess.run(cmd, shell=True)
                os.remove(resized_path)
                GLib.idle_add(self.update_progress_bar, (idx + 1) / 9)

        dialog = Gtk.MessageDialog(
            transient_for=self.window, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
            text="PDF Created",
        )
        dialog.format_secondary_text(f"PDF created as {output_path}")
        dialog.run()
        dialog.destroy()

    def generate_pdf_thread(self, button):
        threading.Thread(target=self.generate_pdf, daemon=True).start()

    def preview_images(self, button):
        folder_path = self.folder_button.get_filename() or self.default_folder
        self.update_preview(folder_path)

    def update_preview(self, folder_path):
        conversion_factor = 300 / 25.4
        page_width_px = int(PAGE_WIDTH_MM * conversion_factor * PREVIEW_SCALE)
        page_height_px = int(PAGE_HEIGHT_MM * conversion_factor * PREVIEW_SCALE)

        # Create an image for preview
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
                if self.horizontal_button.get_active():
                    img = img.rotate(90, expand=True)
                img = img.resize((int(img_width_mm * conversion_factor * PREVIEW_SCALE * WIDTH_ADJUSTMENT),
                                  int(img_height_mm * conversion_factor * PREVIEW_SCALE * HEIGHT_ADJUSTMENT)))
                preview_img.paste(img, (x, y))

        # Convert the Image object to a GdkPixbuf
        buf = BytesIO()
        preview_img.save(buf, format='png')
        buf.seek(0)
        loader = GdkPixbuf.PixbufLoader.new_with_mime_type('image/png')
        loader.write(buf.read())
        loader.close()
        pixbuf = loader.get_pixbuf()

        # Update the preview image
        self.preview_image.set_from_pixbuf(pixbuf)


# Connect signals defined in Glade
builder.connect_signals(PDFGeneratorApp())

Gtk.main()
