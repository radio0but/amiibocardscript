import gi
gi.require_version('Gtk', '3.0')
import requests
import json
import threading
import os
from gi.repository import Gtk, GdkPixbuf, GLib, Pango
# Import the modularized components
from ACDcomponents import ThumbnailBox, ImageButton, AmiiboFilterBox
from ACDutils import fetch_amiibo_data, load_image_data



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