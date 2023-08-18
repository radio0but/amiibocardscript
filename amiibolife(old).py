import gi
import requests
import json
import threading
import os
from gi.repository import Gtk, GdkPixbuf, GLib

gi.require_version('Gtk', '4.0')


class AmiiboApp(Gtk.Application):
    amiibo_images = []
    selected_images = []
    cols = 8
    image_thumbnail_size = 600

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.amiibo.ImageApp", **kwargs)

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Animal Crossing Amiibo Images")
        self.window.set_default_size(800, 600)

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Left pane for the image grid
        scrolled_window = Gtk.ScrolledWindow()
        self.image_grid = Gtk.Grid()
        scrolled_window.set_child(self.image_grid)
        scrolled_window.set_hexpand(True)
        hbox.append(scrolled_window)

        # Right pane for displaying larger image
        self.large_image = Gtk.Image(hexpand=True, vexpand=True)
        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_pane.append(self.large_image)
        hbox.append(right_pane)
        right_pane.set_size_request(int(self.window.get_default_size()[0] * 0.25), -1)

        main_vbox.append(hbox)

        # Bottom bar for the download button and the info label
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.info_label = Gtk.Label(label="0/9 images selected")
        bottom_bar.append(self.info_label)

        # Add the download button below
        self.download_button = Gtk.Button(label="Download Selected Images")
        self.download_button.connect("clicked", self.download_selected_images)
        self.download_button.set_sensitive(False)  # Initially disabled
        bottom_bar.append(self.download_button)

        # Add the deselect button below
        self.deselect_button = Gtk.Button(label="Deselect All")
        self.deselect_button.connect("clicked", self.deselect_all_images)
        bottom_bar.append(self.deselect_button)

        main_vbox.append(bottom_bar)

        self.window.set_child(main_vbox)
        self.window.show()

        # Start a background thread to load images
        threading.Thread(target=self.load_images, daemon=True).start()

    def select_image(self, button, index, image_loader):
        scaled_pixbuf = image_loader.get_pixbuf().scale_simple(int(self.window.get_default_size()[0] * 0.25), int(self.window.get_default_size()[0] * 0.25), GdkPixbuf.InterpType.BILINEAR)
        self.large_image.set_from_pixbuf(scaled_pixbuf)

        if index in self.selected_images:
            self.selected_images.remove(index)
            button.set_child(Gtk.Image.new_from_pixbuf(image_loader.get_pixbuf().scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR)))
        else:
            if len(self.selected_images) < 9:
                self.selected_images.append(index)
                button.set_child(Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file("red-dot.png").scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR)))

        self.update_info_label_and_buttons()

    def deselect_all_images(self, button):
        self.selected_images.clear()
        self.update_grid()
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

        # Notify the user that the download is complete
        dialog = Gtk.MessageDialog(text="Download Complete", buttons=Gtk.ButtonsType.OK, parent=self.window)
        dialog.run()
        dialog.destroy()

    def update_info_label_and_buttons(self):
        # Update the info label
        self.info_label.set_text(f"{len(self.selected_images)}/9 images selected")
        if len(self.selected_images) == 9:
            self.download_button.set_sensitive(True)
        else:
            self.download_button.set_sensitive(False)

    def update_grid(self):
        for index, button in enumerate(self.image_grid.get_children()):
            image_loader = GdkPixbuf.PixbufLoader()
            image_loader.write(requests.get(self.amiibo_images[index]['image']).content)
            image_loader.close()

            if index in self.selected_images:
                button.set_child(Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file("red-dot.png").scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR)))
            else:
                button.set_child(Gtk.Image.new_from_pixbuf(image_loader.get_pixbuf().scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR)))

    def load_images(self):
        response = requests.get('https://www.amiiboapi.com/api/amiibo/?amiiboSeries=Animal%20Crossing')
        amiibo_data = json.loads(response.text)
        self.amiibo_images = amiibo_data['amiibo']

        for index, amiibo in enumerate(self.amiibo_images):
            image_url = amiibo['image']
            print(f"Loading image {index + 1}: {image_url}")
            response = requests.get(image_url)
            image_loader = GdkPixbuf.PixbufLoader()
            image_loader.write(response.content)
            image_loader.close()

            # Run this on the main thread
            GLib.idle_add(self.add_image_to_grid, index, image_loader)

    def add_image_to_grid(self, index, image_loader):
        image_button = Gtk.Button()
        image = Gtk.Image.new_from_pixbuf(image_loader.get_pixbuf().scale_simple(self.image_thumbnail_size, self.image_thumbnail_size, GdkPixbuf.InterpType.BILINEAR))
        image_button.set_child(image)
        image_button.connect("clicked", self.select_image, index, image_loader)
        row = index // self.cols
        col = index % self.cols
        self.image_grid.attach(image_button, col, row, 1, 1)
        self.image_grid.show()


app = AmiiboApp()
app.run()
