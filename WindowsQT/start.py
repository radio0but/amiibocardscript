import subprocess
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtUiTools import QUiLoader

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI from .ui file
        loader = QUiLoader()
        self.ui = loader.load("start.ui", self)
        self.setCentralWidget(self.ui.centralwidget)

        # Connect buttons to functions
        self.ui.download_button.clicked.connect(self.on_downloader_button_clicked)
        self.ui.printprep_button.clicked.connect(self.on_printprep_button_clicked)
        self.ui.print_button.clicked.connect(self.on_print_button_clicked)

    def on_downloader_button_clicked(self):
        subprocess.Popen(["python", "AmiiboCardsDownloader.py"])

    def on_printprep_button_clicked(self):
        subprocess.Popen(["python", "AmiiboCardsPrintPrep.py"])

    def on_print_button_clicked(self):
        output_path = os.path.join("amiibo", "output.pdf")
        if not os.path.exists(output_path):
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Critical)
            dialog.setWindowTitle("File Not Found")
            dialog.setText(f"The file {output_path} does not exist.")
            dialog.setStandardButtons(QMessageBox.Cancel)
            dialog.exec_()
        else:
            os.startfile(output_path)

if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    window.show()
    app.exec_()
