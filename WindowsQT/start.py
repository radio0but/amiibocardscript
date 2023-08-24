import subprocess
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QMessageBox, QWidget

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create widgets and layout
        layout = QVBoxLayout()
        self.download_button = QPushButton("Download Amiibo Cards")
        self.printprep_button = QPushButton("Prepare Amiibo Cards for Print")
        self.print_button = QPushButton("Print Amiibo Cards")

        # Connect download button
        self.download_button.clicked.connect(self.on_downloader_button_clicked)

        # Connect print preparation button
        self.printprep_button.clicked.connect(self.on_printprep_button_clicked)

        # Connect print button
        self.print_button.clicked.connect(self.on_print_button_clicked)

        layout.addWidget(self.download_button)
        layout.addWidget(self.printprep_button)
        layout.addWidget(self.print_button)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        self.show()

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
    app.exec_()

