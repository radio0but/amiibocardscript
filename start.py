import gi
import subprocess
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("window.glade")
        self.window = self.builder.get_object("main_window")
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

        # Connect download button
        self.download_button = self.builder.get_object("download_button")
        self.download_button.connect("clicked", self.on_downloader_button_clicked)

        # Connect print preparation button
        self.printprep_button = self.builder.get_object("printprep_button")
        self.printprep_button.connect("clicked", self.on_printprep_button_clicked)

        # Connect print button
        self.print_button = self.builder.get_object("print_button")
        self.print_button.connect("clicked", self.on_print_button_clicked)

    def on_downloader_button_clicked(self, widget):
        subprocess.Popen(["python", "AmiiboCardsDownloader.py"])

    def on_printprep_button_clicked(self, widget):
        subprocess.Popen(["python", "AmiiboCardsPrintPrep.py"])

    def on_print_button_clicked(self, widget):
        output_path = os.path.join("amiibo", "output.pdf")
        if not os.path.exists(output_path):
            dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "File Not Found")
            dialog.format_secondary_text(f"The file {output_path} does not exist.")
            dialog.run()
            dialog.destroy()
        else:
            subprocess.Popen(["lpr", output_path])

win = MyWindow()
Gtk.main()
