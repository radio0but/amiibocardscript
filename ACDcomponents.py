import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

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

class AmiiboFilterBox(Gtk.Box):
    def __init__(self, search_callback):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Search")
        self.search_entry.connect("changed", search_callback)
        self.pack_start(self.search_entry, False, False, 5)

        self.amiibo_series_filter = Gtk.ComboBoxText()
        self.amiibo_series_filter.connect("changed", search_callback)
        self.pack_start(self.amiibo_series_filter, False, False, 5)
