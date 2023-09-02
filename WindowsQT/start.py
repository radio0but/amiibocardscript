import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QLabel, QWidget
from PySide6.QtGui import QIcon

# You will need to convert these modules to use Qt (PySide6) as well
from AmiiboCardsDownloader import AmiiboApp
from AmiiboCardsPrintPrep import PDFGeneratorApp
from instruction import Instructions
from print import PrintButton

# Main Application Window
class ParentApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amiibo Cards Generator Suite")
        self.setGeometry(100, 100, 800, 600) # X, Y, Width, Height
        
        # Set the window icon
        icon_path = "icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        
        # Assuming the imported components are now QWidget-derived in Qt
        app_one = AmiiboApp()
        app_two = PDFGeneratorApp()
        app_three = PrintButton()
        app_four = Instructions()

        self.tabWidget.addTab(app_one, "Step 1: Cards Downloader")
        self.tabWidget.addTab(app_two, "Step 2: PDF Generator")
        self.tabWidget.addTab(app_three, "Step 3: Print")
        self.tabWidget.addTab(app_four, "Instructions")

app = QApplication(sys.argv)
window = ParentApp()
window.show()
sys.exit(app.exec_())
