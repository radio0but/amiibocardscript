import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os

# Import the modularized components
from AmiiboCardsDownloader import AmiiboApp
from AmiboPrintPrep import PDFGeneratorApp
from instruction import Instructions
from print import PrintButton

# Main Application Window
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
        app_four = Instructions()

        self.notebook.append_page(app_one, Gtk.Label(label="Step 1: Cards Downloader"))
        self.notebook.append_page(app_two, Gtk.Label(label="Step 2: PDF Generator"))
        self.notebook.append_page(app_three, Gtk.Label(label="Step 3 : Print"))
        self.notebook.append_page(app_four, Gtk.Label(label="Instructions"))

win = ParentApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
