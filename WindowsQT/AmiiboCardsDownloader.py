import sys
import json
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                               QHBoxLayout, QLineEdit, QComboBox, QListWidget,
                               QListWidgetItem, QPushButton, QWidget, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QObject, Signal, QRunnable, QThreadPool
from PySide6.QtGui import QPixmap
import os


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


class AmiiboApp(QMainWindow):
    signal_add_thumbnail = Signal(QPixmap, str, str, str, str, str, bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Amiibo App')
        self.setGeometry(100, 100, 800, 600)
        self.selected_images = []
        self.amiibo_images = []
        self.image_thumbnail_size = 100

        main_layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        main_widget = QWidget()

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Amiibo Name")
        self.search_entry.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_entry)

        self.amiibo_series_filter = QComboBox()
        self.amiibo_series_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.amiibo_series_filter)

        main_layout.addLayout(filter_layout)
        content_layout = QHBoxLayout()

        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.select_image)
        content_layout.addWidget(self.image_list)

        details_layout = QVBoxLayout()
        self.large_image_label = QLabel()
        details_layout.addWidget(self.large_image_label)
        self.info_label = QLabel("0/9 images selected")
        details_layout.addWidget(self.info_label)
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_selected_images)
        details_layout.addWidget(self.download_button)
        self.deselect_button = QPushButton("Deselect All")
        self.deselect_button.clicked.connect(self.deselect_all_images)
        details_layout.addWidget(self.deselect_button)
        details_widget = QWidget()
        details_widget.setLayout(details_layout)
        content_layout.addWidget(details_widget)

        main_layout.addLayout(content_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.load_amiibo_series()
        self.signal_add_thumbnail.connect(self.add_thumbnail)

    def load_amiibo_series(self):
        response = requests.get('https://www.amiiboapi.com/api/amiibo/')
        amiibo_data = json.loads(response.text)
        self.amiibo_images = amiibo_data['amiibo']
        amiibo_series = set()
        for amiibo in self.amiibo_images:
            amiibo_series.add(amiibo.get('amiiboSeries', 'Unknown'))

        self.amiibo_series_filter.addItem("Select Amiibo Series")
        for series in sorted(amiibo_series):
            self.amiibo_series_filter.addItem(series)

    def apply_filters(self):
        self.image_list.clear()
        search_query = self.search_entry.text().strip().lower()
        amiibo_series_filter = self.amiibo_series_filter.currentText()

        if amiibo_series_filter == "Select Amiibo Series":
            return

        for index, amiibo in enumerate(self.amiibo_images):
            if search_query and search_query not in amiibo['name'].lower():
                continue

            if amiibo_series_filter and amiibo_series_filter not in amiibo['amiiboSeries']:
                continue

            thumbnail_url = amiibo['image']
            name = amiibo['name']
            series = amiibo['amiiboSeries']
            character = amiibo['character']
            amiibo_type = amiibo['type']

            selected = thumbnail_url in self.selected_images

            runnable = ImageLoader(self.load_image, thumbnail_url, name, series, character, amiibo_type, self.image_thumbnail_size, selected)
            QThreadPool.globalInstance().start(runnable)

    def load_image(self, url, name, series, character, amiibo_type, size=None, selected=False):
        response = requests.get(url)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        if size:
            pixmap = pixmap.scaledToWidth(size)
        self.signal_add_thumbnail.emit(pixmap, name, series, character, amiibo_type, url, selected)

    def add_thumbnail(self, pixmap, name, series, character, amiibo_type, url, selected):
        thumbnail = ThumbnailBox(pixmap, name, series, character, amiibo_type, selected)
        item = QListWidgetItem()
        item.setSizeHint(thumbnail.sizeHint())
        self.image_list.addItem(item)
        self.image_list.setItemWidget(item, thumbnail)
        item.setData(Qt.UserRole, url)

    def download_selected_images(self):
        amiibo_folder = "amiibo"
        if not os.path.exists(amiibo_folder):
            os.makedirs(amiibo_folder)

        for index, url in enumerate(self.selected_images):
            response = requests.get(url)
            with open(f"{amiibo_folder}/image{index + 1}.png", "wb") as f:
                f.write(response.content)

    def select_image(self, item):
        url = item.data(Qt.UserRole)
        if url in self.selected_images:
            self.selected_images.remove(url)
        else:
            if len(self.selected_images) < 9:
                self.selected_images.append(url)
        self.apply_filters()
        self.update_details()

    def update_details(self):
        num_images = len(self.selected_images)
        self.info_label.setText(f"{num_images}/9 images selected")
        self.large_image_label.clear()
        if self.selected_images:
            response = requests.get(self.selected_images[-1])
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.large_image_label.setPixmap(pixmap)

    def deselect_all_images(self):
        self.selected_images.clear()
        self.apply_filters()
        self.update_details()

    def run(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AmiiboApp()
    window.run()
    sys.exit(app.exec())
