#!/bin/bash

# Detect Linux Distribution
OS=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
elif type lsb_release >/dev/null 2>&1; then
    OS=$(lsb_release -si)
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    OS=$DISTRIB_ID
else
    OS=$(uname -s)
fi

echo "Detected OS: $OS"

# Install dependencies based on OS
if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
    sudo apt-get update
    sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pip imagemagick unzip
    pip3 install Pillow requests

elif [[ $OS == *"Fedora"* ]]; then
    sudo dnf install -y python3-gobject python3-cairo-gobject gtk3 python3-pip ImageMagick unzip
    pip3 install Pillow requests

elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"RedHat"* ]]; then
    sudo yum install -y python3-gobject python3-cairo-gobject gtk3 python3-pip ImageMagick unzip
    pip3 install Pillow requests

elif [[ $OS == *"Arch Linux"* ]] || [[ $OS == *"Manjaro"* ]]; then
    sudo pacman -Syu --noconfirm python-gobject python-cairo gobject-introspection-runtime gtk3 python-pip imagemagick unzip
    pip3 install Pillow requests

else
    echo "Sorry, this script does not support the detected OS."
    exit 1
fi

# Define the installation path in the user's home directory
INSTALL_PATH="$HOME/amiiboGenerator"

# Remove the directory if it already exists
if [ -d "$INSTALL_PATH" ]; then
    rm -rf "$INSTALL_PATH"
fi

# Download and unzip the release.zip file
wget https://github.com/radio0but/amiibocardscript/releases/download/v1.1/release.zip
mkdir -p "$INSTALL_PATH"
unzip release.zip -d "$INSTALL_PATH"

# Create a wrapper script to execute the Python script
echo '#!/bin/bash' > "$HOME/amiiboGenerator.sh"
echo "cd $INSTALL_PATH" >> "$HOME/amiiboGenerator.sh"
echo "exec python3 $INSTALL_PATH/start.py \"\$@\"" >> "$HOME/amiiboGenerator.sh"
chmod +x "$HOME/amiiboGenerator.sh"

# Create desktop entry
echo '[Desktop Entry]' > "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo 'Name=Amiibo Generator' >> "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo 'Comment=Start Amiibo Generator' >> "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo "Exec=$HOME/amiiboGenerator.sh" >> "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo "Icon=$INSTALL_PATH/icon.png" >> "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo 'Terminal=false' >> "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo 'Type=Application' >> "$HOME/.local/share/applications/amiiboGenerator.desktop"
echo 'Categories=Utility;' >> "$HOME/.local/share/applications/amiiboGenerator.desktop"

echo "Installation complete. You can run the program with the command '$HOME/amiiboGenerator.sh' or from the application menu."
