# Amiibo Card Generator Suite

This project contains two Python applications for creating ready-to-print PDFs of Amiibo cards. It includes `AmiiboCardsDownloader.py` for downloading and selecting images and `AmiiboCardsPrintPrep.py` for generating the final PDF file. This project uses AmiiboAPI for data. The AmiiboCardsPrintPrep.py is specifically calibrated for NFC cards 5.44cm x 8.55cm tested on an HP DeskJet 3630 printer.

![Alt text](https://imgur.com/LImBoSo.png "a title")
![Alt text](https://imgur.com/kKbns51.png "a title")

## Installation

### Windows

1. Install Python from [the official website](https://www.python.org/downloads/).
2. Install GTK 3 from [this link](https://www.gtk.org/docs/installations/windows/).
3. Install Python dependencies with the following command:

```bash
pip install requests pillow PyGObject
```
### Ubuntu/Fedora

1. Install Python and GTK 3 with:

```bash
sudo apt-get install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 # Ubuntu
sudo dnf install python3 gtk3 python3-gobject python-pillow # Fedora
```

2. Install Python dependencies:

```bash
pip3 install requests
```
### Arch

1. Install Python and GTK 3 with:

```bash
sudo pacman -S python-gobject python-pillow gtk3
```

2. Install Python dependencies:

```bash
pip install requests
```

### MacOS

1. Install Homebrew if you don't have it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Python and GTK:

```bash
brew install python gtk+3 pygobject3
```

3. Install Python dependencies:

```bash
pip install requests pillow
```
## Usage

1. **Downloading and Selecting Images**: Run `AmiiboCardsDownloader.py` to download and select 9 images.

```bash
python AmiiboCardsDownloader.py
```

Select 9 images by clicking on them and click the download button when they are chosen. You can find them more quickly by filtering by Series or by name using the search bar. The application is still unstable as there are many amiibo to load. The filter function cannot filter the images until everything is downloaded.

2. **PDF Creation**: Run `AmiiboCardsPrintPrep.py` to open the PDF creation interface.

```bash
python AmiiboCardsPrintPrep.py
```

Choose the orientation, preview, and generate the PDF; the images will be stretched to fill the card. If you did not use AmiiboCardsDownloader.py and downloaded the images manually, you can select the folder containing them. Ensure you have named the images as image1.png, image2.png, etc.
