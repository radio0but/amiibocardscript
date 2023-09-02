from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
import os
import sys
import subprocess

class PrintButton(QWidget):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("print_button.ui", self)
        self.setLayout(self.ui.layout())

        # Connect signals
        self.ui.print_button.clicked.connect(self.on_print_button_clicked)
        self.ui.pdf_button.clicked.connect(self.on_pdf_button_clicked)
        self.ui.pdf_win_button.clicked.connect(self.on_pdf_win_button_clicked)

    def on_print_button_clicked(self):
        output_path = os.path.join("amiibo", "output.pdf")
        self.open_or_print(output_path, ["lpr", output_path])

    def on_pdf_button_clicked(self):
        output_path = os.path.join("amiibo", "output.pdf")
        self.open_or_print(output_path, ["xdg-open", output_path])

    def on_pdf_win_button_clicked(self):
        output_path = os.path.join("amiibo", "output.pdf")
        self.open_or_print_windows(output_path)

    def open_or_print(self, path, command):
        if not os.path.exists(path):
            QMessageBox.critical(self, "File Not Found", f"The file {path} does not exist.")
        else:
            subprocess.Popen(command)

    def open_or_print_windows(self, path):
        if not os.path.exists(path):
            QMessageBox.critical(self, "File Not Found", f"The file {path} does not exist.")
        else:
            os.startfile(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PrintButtonWidget()
    window.show()
    sys.exit(app.exec_())
