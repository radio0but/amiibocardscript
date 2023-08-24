@echo off

echo Installing dependencies...

python.exe -m pip install --upgrade pip
python.exe -m pip install requests
python.exe -m pip install pillow
python.exe -m pip install pyside6

echo Dependencies installed successfully!
