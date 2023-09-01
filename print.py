import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import subprocess

class PrintButton(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.builder = Gtk.Builder()
        self.builder.add_from_file("print_button.glade")
        
        self.main_box = self.builder.get_object("main_box")
        self.print_button = self.builder.get_object("print_button")
        self.pdf_button = self.builder.get_object("pdf_button")
        
        self.print_button.connect("clicked", self.on_print_button_clicked)
        self.pdf_button.connect("clicked", self.on_pdf_button_clicked)
        
        self.add(self.main_box)

    def on_print_button_clicked(self, widget):
        output_path = os.path.join("amiibo", "output.pdf")
        self.open_or_print(output_path, ["lpr", output_path])

    def on_pdf_button_clicked(self, widget):
        
        output_path = os.path.join("amiibo", "output.pdf")
        self.open_or_print(output_path, ["xdg-open", output_path])

    def open_or_print(self, path, command):
        if not os.path.exists(path):
            dialog = Gtk.MessageDialog(self.get_toplevel(), 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "File Not Found")
            dialog.format_secondary_text(f"The file {path} does not exist.")
            dialog.run()
            dialog.destroy()
        else:
            subprocess.Popen(command)



