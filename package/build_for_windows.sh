#!/bin/sh
EXEC_DIR=$(pwd)

DIR=$(mktemp -d /tmp/manuskript-windows.XXXXXX)
PREFIX=$DIR/.wine

# Install Python:
PY_DOWNLOAD="https://www.python.org/ftp/python/3.8.9/python-3.8.9.exe"
PY_SETUP=$(echo $PY_DOWNLOAD | tr '/' ' ' | awk '{ print $(NF) }')

if [ ! -e $PY_SETUP ]; then
	wget $PY_DOWNLOAD
fi

WINEPREFIX=$PREFIX WINEARCH="win32" wine $PY_SETUP /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

# Install Pandoc:
PAN_DOWNLOAD="https://github.com/jgm/pandoc/releases/download/2.13/pandoc-2.13-windows-x86_64.msi"
PAN_SETUP=$(echo $PAN_DOWNLOAD | tr '/' ' ' | awk '{ print $(NF) }')

if [ ! -e $PAN_SETUP ]; then
	wget $PAN_DOWNLOAD
fi

WINEPREFIX=$PREFIX WINEARCH="win32" wine $PAN_SETUP /qn /norestart

# Install most dependencies with pip:
cd $PREFIX/drive_c/Program\ Files/Python38-32/

pip_install() {
	WINEPREFIX=$PREFIX WINEARCH="win32" wine python.exe Scripts/pip.exe install $@
}

# Upgrade pip to mitigate problems:
pip_install --upgrade pip

# Install required dependencies:
pip_install pyinstaller
pip_install lxml
pip_install PyQt5

# Install optional dependencies:
pip_install pyenchant
pip_install pyspellchecker
pip_install symspellpy
pip_install language_tool_python
pip_install markdown

# Clone the repository from Github:
REPOSITORY="https://github.com/olivierkes/manuskript.git"

cd $DIR
git clone $REPOSITORY
cd manuskript

PKG_VERSION=$(grep -E "__version__.*\".*\"" "manuskript/version.py" | cut -d\" -f2)

# Run PyInstaller to create the build:
WINEPREFIX=$PREFIX WINEARCH="win32" wine pyinstaller manuskript.spec
cat build/manuskript/warn-manuskript.txt

cd dist/manuskript

# Remove this library (causing weird bluetooth problems):
### comment: We don't need bluetooth anyway... ^^'
rm Qt5Bluetooth.dll

# Remove unnecessary libraries:
rm api-ms-win-*

# Test Manuskript:
### comment: Seems to work fine...
#WINEPREFIX=$PREFIX WINEARCH="win32" wine manuskript.exe

ZIP_NAME=manuskript-$PKG_VERSION-win32.zip

# Package everything together:
cd ..
zip -r $ZIP_NAME manuskript
mv $ZIP_NAME $EXEC_DIR

# Cleanup everything:
### comment: removing the local git repository 
###          requires write permissions...
chmod +w -R $DIR/manuskript
rm -r $DIR
