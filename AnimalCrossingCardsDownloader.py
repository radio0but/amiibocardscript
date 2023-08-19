import gi
gi.require_version('Gtk', '3.0')
import requests
import json
import threading
import os
from gi.repository import Gtk, GdkPixbuf, GLib

class ImageButton(Gtk.Button):
    def __init__(self, image):
        super().__init__()
        self.image_widget = image
        self.add(self.image_widget)

    def get_image_widget(self):
        return self.image_widget

class AmiiboApp(Gtk.Application):

    def __init__(self):
        super(AmiiboApp, self).__init__()
        self.amiibo_images = []
        self.selected_images = []
        self.image_buttons = []
        self.image_thumbnail_size = 200

    def do_activate(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("image_parser.glade")

        self.window = self.builder.get_object("window")
        self.window.set_application(self)
        self.window.show_all()

        self.image_listbox = self.builder.get_object("image_listbox")
        self.large_image = self.builder.get_object("large_image")
        self.info_label = self.builder.get_object("info_label")
        self.download_button = self.builder.get_object("download_button")
        self.deselect_button = self.builder.get_object("deselect_button")

        self.download_button.connect("clicked", self.download_selected_images)
        self.deselect_button.connect("clicked", self.deselect_all_images)

        threading.Thread(target=self.load_images, daemon=True).start()

    def on_button_clicked(self, button, index, image_loader):
        scaled_pixbuf = image_loader.get_pixbuf().scale_simple(300, 300, GdkPixbuf.InterpType.BILINEAR)
        self.large_image.set_from_pixbuf(scaled_pixbuf)

        image_widget = button.get_image_widget()
        if index in self.selected_images:
            self.selected_images.remove(index)
            image_widget.set_from_pixbuf(image_loader.get_pixbuf().scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR))
        else:
            if len(self.selected_images) < 9:
                overlay = GdkPixbuf.Pixbuf.new_from_file("red_dot.png")
                composite_pixbuf = image_loader.get_pixbuf().scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR).copy()
                overlay.composite(composite_pixbuf, 0, 0, self.image_thumbnail_size, self.image_thumbnail_size, 0, 0, 1, 1, GdkPixbuf.InterpType.BILINEAR, 255)
                image_widget.set_from_pixbuf(composite_pixbuf)
                self.selected_images.append(index)

        self.update_info_label_and_buttons()

    def download_selected_images(self, button):
        download_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "amiibo")
        os.makedirs(download_folder, exist_ok=True)

        for idx, index in enumerate(self.selected_images):
            amiibo = self.amiibo_images[index]
            image_url = amiibo['image']
            response = requests.get(image_url)
            file_path = os.path.join(download_folder, f'image{idx + 1}.png')
            with open(file_path, 'wb') as f:
                f.write(response.content)

        dialog = Gtk.MessageDialog(text="Download Complete", buttons=Gtk.ButtonsType.OK, parent=self.window)
        dialog.run()
        dialog.destroy()
        self.deselect_all_images(None)

    def update_info_label_and_buttons(self):
        self.info_label.set_text(f"{len(self.selected_images)}/9 images selected")
        self.download_button.set_sensitive(len(self.selected_images) == 9)

    def load_images(self):
        response = requests.get('https://www.amiiboapi.com/api/amiibo/?amiiboSeries=Animal%20Crossing')
        amiibo_data = json.loads(response.text)
        self.amiibo_images = amiibo_data['amiibo']

        for index, amiibo in enumerate(self.amiibo_images):
            image_url = amiibo['image']
            response = requests.get(image_url)
            image_loader = GdkPixbuf.PixbufLoader()
            image_loader.write(response.content)
            image_loader.close()

            GLib.idle_add(self.add_image_to_listbox, index, amiibo, image_loader)

    def deselect_all_images(self, button):
        self.selected_images.clear()
        for row in self.image_listbox.get_children():
            row.destroy()
        threading.Thread(target=self.load_images, daemon=True).start()
        self.update_info_label_and_buttons()

    def add_image_to_listbox(self, index, amiibo, image_loader):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        image = Gtk.Image.new_from_pixbuf(image_loader.get_pixbuf().scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR))
        button = ImageButton(image)
        button.connect("clicked", self.on_button_clicked, index, image_loader)
        self.image_buttons.append(button)
        hbox.pack_start(button, False, False, 0)
        details_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        name_label = Gtk.Label(amiibo['name'])
        amiibo_series_label = Gtk.Label(f"Amiibo Series: {amiibo['amiiboSeries']}")
        character_label = Gtk.Label(f"Character: {amiibo['character']}")
        game_series_label = Gtk.Label(f"Game Series: {amiibo['gameSeries']}")
        type_label = Gtk.Label(f"Type: {amiibo['type']}")
        details_vbox.pack_start(name_label, True, True, 0)
        details_vbox.pack_start(amiibo_series_label, True, True, 0)
        details_vbox.pack_start(character_label, True, True, 0)
        details_vbox.pack_start(game_series_label, True, True, 0)
        details_vbox.pack_start(type_label, True, True, 0)
        hbox.pack_start(details_vbox, True, True, 0)
        self.image_listbox.add(hbox)
        hbox.show_all()

app = AmiiboApp()
app.run()
