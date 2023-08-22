import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
import requests
import json
import threading
import os

class ThumbnailBox(Gtk.Box):
    def __init__(self, image_data, name, series, character, amiibo_type):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.image = Gtk.Image.new_from_pixbuf(image_data)
        self.pack_start(self.image, False, False, 5)
        self.label_name = Gtk.Label(name)
        self.pack_start(self.label_name, False, False, 5)
        self.label_series = Gtk.Label(f"Series: {series}")
        self.pack_start(self.label_series, False, False, 5)
        self.label_character = Gtk.Label(f"Character: {character}")
        self.pack_start(self.label_character, False, False, 5)
        self.label_type = Gtk.Label(f"Type: {amiibo_type}")
        self.pack_start(self.label_type, False, False, 5)

    def get_image(self):
        return self.image

class ImageButton(Gtk.Button):
    def __init__(self, thumbnail, url):
        super().__init__()
        self.thumbnail_widget = thumbnail
        self.add(self.thumbnail_widget)
        self.url = url

    def get_thumbnail_widget(self):
        return self.thumbnail_widget

    def get_url(self):
        return self.url

class AmiiboApp(Gtk.Application):
    def __init__(self):
        super(AmiiboApp, self).__init__()
        self.amiibo_images = []
        self.selected_images = []
        self.image_thumbnail_size = 100

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Amiibo App")
        self.window.set_default_size(800, 600)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(main_box)

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

        self.window.show_all()

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

if __name__ == '__main__':
    app = AmiiboApp()
    app.run()