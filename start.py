import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Pango
import requests
import json
import threading
import os
from PIL import Image
from io import BytesIO
import subprocess

# Import the modularized components
from ACDcomponents import ThumbnailBox, ImageButton, AmiiboFilterBox
from ACDutils import fetch_amiibo_data, load_image_data

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

# First application (button)
class AmiiboApp(Gtk.Box):
    def __init__(self):
        super(AmiiboApp, self).__init__(orientation=Gtk.Orientation.VERTICAL)

        self.amiibo_images = []
        self.selected_images = []
        self.image_thumbnail_size = 100
        
        main_box = self  # Now, AmiiboApp itself is the main box

        # Start - Logo and Label code
        logo_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(logo_label_box, False, False, 10)

        logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file("Amiibo_logo.png")
        logo_image = Gtk.Image.new_from_pixbuf(logo_pixbuf)
        logo_label_box.pack_start(logo_image, False, False, 0)

        title_label = Gtk.Label("Cards Downloader")
        title_label.set_size_request(300, 0)

        font_desc = title_label.get_pango_context().get_font_description()
        font_desc.set_size(18 * Pango.SCALE)
        title_label.modify_font(font_desc)

        logo_label_box.pack_start(title_label, False, False, 0)

        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(filter_box, False, False, 5)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search")
        self.search_entry.connect("changed", self.apply_filters)
        filter_box.pack_start(self.search_entry, False, False, 5)

        self.amiibo_series_filter = Gtk.ComboBoxText()
        self.amiibo_series_filter.connect("changed", self.apply_filters)
        filter_box.pack_start(self.amiibo_series_filter, False, False, 5)

        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.pack_start(content_box, True, True, 0)

        scrolled_window = Gtk.ScrolledWindow()
        self.image_listbox = Gtk.ListBox()
        scrolled_window.add(self.image_listbox)
        content_box.pack_start(scrolled_window, True, True, 5)

        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.large_image = Gtk.Image()
        

        details_box.pack_start(self.large_image, True, True, 5)
        self.info_label = Gtk.Label.new("0/9 images selected")
        details_box.pack_start(self.info_label, False, False, 5)
        self.download_button = Gtk.Button(label="Download")
        self.download_button.connect("clicked", self.download_selected_images)
        details_box.pack_start(self.download_button, False, False, 5)
        self.deselect_button = Gtk.Button(label="Deselect All")
        self.deselect_button.connect("clicked", self.deselect_all_images)
        details_box.pack_start(self.deselect_button, False, False, 5)

        content_box.pack_start(details_box, False, False, 5)
        self.show_all()

        threading.Thread(target=self.load_images, daemon=True).start()

    def load_images(self):
        response = requests.get('https://www.amiiboapi.com/api/amiibo/')
        amiibo_data = json.loads(response.text)
        self.amiibo_images = amiibo_data['amiibo']

        amiibo_series = set()
        for amiibo in self.amiibo_images:
            amiibo_series.add(amiibo.get('amiiboSeries', 'Unknown'))

        GLib.idle_add(self.amiibo_series_filter.append_text, "Select Amiibo Series")
        for series in sorted(amiibo_series):
            GLib.idle_add(self.amiibo_series_filter.append_text, series)

        GLib.idle_add(self.amiibo_series_filter.set_active, 0)

    def apply_filters(self, *args):
        search_query = self.search_entry.get_text().strip().lower()
        amiibo_series_filter = self.amiibo_series_filter.get_active_text()

        if amiibo_series_filter == "Select Amiibo Series":
            amiibo_series_filter = None

        for row in self.image_listbox.get_children():
            row.destroy()

        for index, amiibo in enumerate(self.amiibo_images):
            if search_query and search_query not in amiibo['name'].lower():
                continue

            if amiibo_series_filter and amiibo_series_filter not in amiibo['amiiboSeries']:
                continue

            thumbnail_url = amiibo['image']
            name = amiibo['name']
            series = amiibo['amiiboSeries']
            character = amiibo['character']
            amiibo_type = amiibo['type']

            def create_row(image_data, name, series, character, amiibo_type, url):
                thumbnail = ThumbnailBox(image_data, name, series, character, amiibo_type)
                image_button = ImageButton(thumbnail, url)
                image_button.connect("clicked", self.select_image, amiibo)
                self.image_listbox.add(image_button)
                image_button.show_all()

            threading.Thread(target=self.load_image_thumbnail, args=(thumbnail_url, name, series, character, amiibo_type, create_row), daemon=True).start()

    def load_image_thumbnail(self, url, name, series, character, amiibo_type, callback):
        image_data = self.load_image_data(url, self.image_thumbnail_size)
        GLib.idle_add(callback, image_data, name, series, character, amiibo_type, url)

    def load_image_data(self, url, size=None):
        response = requests.get(url)
        loader = GdkPixbuf.PixbufLoader()
        loader.write(response.content)
        loader.close()

        pixbuf = loader.get_pixbuf()
        if size:
            aspect_ratio = pixbuf.get_height() / pixbuf.get_width()
            new_height = size * aspect_ratio
            pixbuf = pixbuf.scale_simple(size, int(new_height), GdkPixbuf.InterpType.BILINEAR)

        return pixbuf

    def select_image(self, button, amiibo):
        thumbnail_box = button.get_thumbnail_widget()
        image_widget = thumbnail_box.get_image()
        url = button.get_url()

        if len(self.selected_images) >= 9 and image_widget.get_opacity() == 1:
            return

        if image_widget.get_opacity() < 1:
            image_widget.set_opacity(1)
            self.selected_images.remove(url)
        else:
            image_widget.set_opacity(0.3)
            self.selected_images.append(url)
            large_image_data = self.load_image_data(url)
            self.large_image.set_from_pixbuf(large_image_data)
            self.large_image.set_size_request(300, -1)
            self.large_image.props.icon_size = Gtk.IconSize.DIALOG

        self.update_info_label()
        self.download_button.set_sensitive(len(self.selected_images) == 9)

    def deselect_all_images(self, button):
        for row in self.image_listbox.get_children():
            image_button = row.get_children()[0]
            thumbnail_box = image_button.get_thumbnail_widget()
            image_widget = thumbnail_box.get_image()
            image_widget.set_opacity(1)

        self.selected_images.clear()
        self.update_info_label()
        self.download_button.set_sensitive(False)

    def download_selected_images(self, button):
        amiibo_folder = "amiibo"
        if not os.path.exists(amiibo_folder):
            os.makedirs(amiibo_folder)

        for index, url in enumerate(self.selected_images):
            image_data = self.load_image_data(url)
            file_path = os.path.join(amiibo_folder, f"image{index+1}.png")
            image_data.savev(file_path, 'png', [], [])

        print(f"{len(self.selected_images)} images downloaded to {amiibo_folder}")

    def update_info_label(self):
        self.info_label.set_text(f"{len(self.selected_images)}/9 images selected")
# Second application (label)
class PDFGeneratorApp(Gtk.Box):
    def __init__(self):
        super(PDFGeneratorApp, self).__init__(orientation=Gtk.Orientation.VERTICAL)

        # Load the related components for this app from the Glade file
        builder = Gtk.Builder()
        builder.add_from_file("pdf_generator.glade")
        
        self.add(builder.get_object("window1"))  # Assuming "main_layout" is the top-level container in the glade for this app

        # Get objects from Glade file
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
        #self.window.connect("destroy", Gtk.main_quit)
        #self.window.show_all()

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

class PrintButton(Gtk.Box):
    def __init__(self):
        super().__init__(spacing=10)

        # Create the button with a label
        self.button = Gtk.Button(label="")

        # Load the image icon
        icon_path = "printprep_icon.png"
        if os.path.exists(icon_path):
            image = Gtk.Image.new_from_file(icon_path)
            self.button.set_image(image)
            self.button.set_always_show_image(True)

        # Connect the button click event
        self.button.connect("clicked", self.on_button_clicked)

        # Pack the button to the box
        self.pack_start(self.button, True, True, 0)
    
    def on_button_clicked(self, widget):
        output_path = os.path.join("amiibo", "output.pdf")
        if not os.path.exists(output_path):
            dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "File Not Found")
            dialog.format_secondary_text(f"The file {output_path} does not exist.")
            dialog.run()
            dialog.destroy()
        else:
            subprocess.Popen(["lpr", output_path])
# Parent application with tabs
class ParentApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Amiibo Cards Generator Suite")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        # Set the window icon
        icon_path = "icon.png"
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        app_one = AmiiboApp()
        app_two = PDFGeneratorApp()
        app_three = PrintButton()

        self.notebook.append_page(app_one, Gtk.Label(label="Step 1: Cards Downloader"))
        self.notebook.append_page(app_two, Gtk.Label(label="Step 2: PDF Generator"))
        self.notebook.append_page(app_three, Gtk.Label(label="Step 3 : Print"))


win = ParentApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
