# Amiibo Cards Generator Suite

This project contains two Python applications for creating ready-to-print PDFs of Amiibo cards. It includes `AmiiboCardsDownloader.py` for downloading and selecting images and `AmiiboCardsPrintPrep.py` for generating the final PDF file. This project uses AmiiboAPI for data. The AmiiboCardsPrintPrep.py is specifically calibrated for NFC cards 5.44cm x 8.55cm tested on an HP DeskJet 3630 printer.

Big new the GTK version is no a one window application !!!!!

Making amiibo cards sticker is now more straightforward, thanks to a new launcher script(start.py) that guides users through the process.

### For Linux Users:

Simply download and run installer.sh. This will install the software on your system.
In most desktop environments (DEs), the amiiboGenerator app will be visible in the utility section of your application menu.

The App gets installed in the user's home directory because the app is moving creating deleting file in its folder. It needs too much permissions to be in a System folder.

Thats the GTK version This is the default version for linux (install.sh)

![](AmiiboGen.GIF)


Thats the Qt Version on linux
![Alt text](https://imgur.com/OGzC8Vu.png "Qt Version on Linux")

### For Windows Users:

I've provided a Windows installer named AmiiboCardGeneratorSuite_Install.exe.
This version utilizes QT, which offers a smoother experience on Windows.
Please ensure that Python is installed on your system. Also, make sure it's correctly configured in the Path as python.exe. 

The App as to be installed in the user's directory because the app is moving creating 
 and deleting file in its folder. It needs too much permissions to be in a System folder.

![Alt text](https://imgur.com/Jp1aKdv.png "Qt Version on Windows")

## Adding Python and pip to PATH on Windows

1. First, ensure that Python is installed. If not, download the installer from [the official website](https://www.python.org/downloads/).
   
   **Note**: During the installation of Python, there's an option at the bottom of the installation window that says "Add Python to PATH." If you select this, you can skip the manual steps below.

2. If you've already installed Python without adding it to PATH, follow these steps:

   a. Open the `Start` menu, type `Environment Variables`, and select `Edit the system environment variables`.
   
   b. In the `System Properties` window, click the `Environment Variables` button.
   
   c. Under `User variables` or `System variables`, find the `PATH` variable and select it. Click the `Edit` button.
   
   d. In the `Edit Environment Variable` window, click the `New` button and paste in the path to your Python's directory (typically `C:\PythonXX`, where `XX` is the version number, like `C:\Python39`).
   
   e. Click `New` again and add the path to the `Scripts` directory inside your Python directory (typically `C:\PythonXX\Scripts`).
   
   f. Click `OK` to close each of the windows.

3. To verify that Python and pip are now part of your PATH, open a new command prompt and type:

```bash
python.exe --version
pip.exe --version
```

You should see the versions of Python and pip displayed. If not, ensure that you've added the correct paths in step 2.


## Installation from source (GTK Version)

### Windows

these instruction are for executing the GTK version on windows for advance user only otherwize use the Qt version. 

1. Install Python from [the official website](https://www.python.org/downloads/).
2. Install GTK 3 from [this link](https://www.gtk.org/docs/installations/windows/).
3. Install Python dependencies with the following command:

You might also be able to use WSL

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

## Installation from source (Qt Version)

### Windows

These instructions are for executing the Qt version on Windows for advanced users. If unsure, use the available installer. 

1. Install Python from [the official website](https://www.python.org/downloads/).
2. Install PySide6 and other required packages:

```bash
pip install PySide6 requests pillow
```

### Ubuntu/Fedora

1. Install Python and necessary Qt dependencies:

```bash
sudo apt-get install python3 python3-pip qttools5-dev-tools # Ubuntu
sudo dnf install python3 python3-pip qt5-qttools-devel # Fedora
```

2. Install Python dependencies:

```bash
pip3 install PySide6 requests pillow
```

### Arch

1. Install Python and necessary Qt dependencies:

```bash
sudo pacman -S python-pip qt5-tools
```

2. Install Python dependencies:

```bash
pip install PySide6 requests pillow
```

### MacOS

1. Install Homebrew if you don't have it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Python and necessary Qt tools:

```bash
brew install python pyqt@5
```

3. Install Python dependencies:

```bash
pip install PySide6 requests pillow
```


## Usage

1. Start the launcher(Qt) or Main app(GTK) with the folowing command
```bash
python start.py
```




# Terms & Conditions

By using the **Amiibo Cards Generator Suite** (hereinafter referred to as the "App"), you hereby accept the following terms and conditions:

- The App, **Amiibo Cards Generator Suite**, has no affiliation with Nintendo, amiiboAPI, or any other companies that own the rights to them.
  
- Reports or information collected by Nintendo, amiiboAPI, or the respective companies that own the rights are not our responsibility.

- The user agrees that the use of this App is entirely at the user’s own risk.

- You will require your end users to comply with (and not knowingly enable them to violate) applicable law, regulation, and these Terms.

- You will comply with all applicable laws, regulations, and third-party rights (including, without limitation, laws regarding the import or export of data or software, privacy, and local laws). You will not use the App to encourage or promote illegal activity or violation of third-party rights.

- These Terms and Conditions are subject to change without notice, from time to time, in our sole discretion.
