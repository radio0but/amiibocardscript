from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader

class Instructions(QWidget):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        ui_path = "instructions.ui"  # Path to the UI file
        self.ui = loader.load(ui_path, self)
        self.setLayout(self.ui.layout())  # Set the layout of the loaded UI to the widget


