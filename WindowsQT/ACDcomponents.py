from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QRunnable






class ImageLoader(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(ImageLoader, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.function(*self.args, **self.kwargs)


class ThumbnailBox(QWidget):
    def __init__(self, image, name, series, character, amiibo_type, selected=False):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel()
        if selected:
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.5)
            self.label.setGraphicsEffect(effect)
        self.label.setPixmap(image)
        layout.addWidget(self.label)
        layout.addWidget(QLabel(name))
        layout.addWidget(QLabel(f"Series: {series}"))
        layout.addWidget(QLabel(f"Character: {character}"))
        layout.addWidget(QLabel(f"Type: {amiibo_type}"))
        self.setLayout(layout)