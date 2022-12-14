#!/bin/bashwine
EXEC_DIR=$(pwd)

DIR=$(mktemp -d /tmp/manuskript-windows.XXXXXX)
PREFIX=$DIR/.wine

BUILD_ARCH="win64" #win32, win64
PY_VERSION="3.9.2" #Version must always be three digirs to comply with PY_DIR for some reason.  idk.

PY_NAME="python-$PY_VERSION"

if [ "$BUILD_ARCH" = "win64" ]; then
	PY_NAME="$PY_NAME-amd64"
fi

# Install Python:
PY_DOWNLOAD="https://www.python.org/ftp/python/$PY_VERSION/$PY_NAME.exe"
PY_SETUP=$(echo $PY_DOWNLOAD | tr '/' ' ' | awk '{ print $(NF) }')

if [ ! -e $PY_SETUP ]; then
	wget $PY_DOWNLOAD
fi

# Need to init the wineboot _first_ it seems. 
# https://forum.manjaro.org/t/wine-could-not-load-kernel32-dll-status-c0000135/69811/2
# https://github.com/ValveSoftware/Proton/issues/4269#issuecomment-757346213
# https://github.com/Frogging-Family/community-patches/issues/75
# https://bugs.winehq.org/show_bug.cgi?id=51086

echo TEST!!! LISTING WINE PREFIX AND BUILDARCH
echo $PREFIX $BUILDARCH

WINEARCH=$BUILD_ARCH winecfg
WINEARCH=$BUILD_ARCH wineboot --init

WINEARCH=$BUILD_ARCH xvfb-run -s '-screen 0 1920x1080x24 +extension GLX' wine64 $PY_SETUP /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1

# Install Pandoc:
PAN_DOWNLOAD="https://github.com/jgm/pandoc/releases/download/2.16.1/pandoc-2.16.1-windows-x86_64.msi"

PAN_SETUP=$(echo $PAN_DOWNLOAD | tr '/' ' ' | awk '{ print $(NF) }')

if [ ! -e $PAN_SETUP ]; then
	wget $PAN_DOWNLOAD
fi

wine $PAN_SETUP /qn /norestart

PY_DIR="Python$(echo $PY_VERSION | sed -e s/\\./\ /g - | awk '{ print $1$2$3 }')"

if [ "$BUILD_ARCH" = "win32" ]; then
	PY_DIR="$PY_DIR-32"
fi

# Install most dependencies with pip:
cd $PREFIX/drive_c/Program\ Files/$PY_DIR/

pip_install() {
	wine python.exe Scripts/pip.exe install $@
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
xvfb-run -s '-screen 0 1920x1080x24 +extension GLX' wine pyinstaller manuskript.spec
cat build/manuskript/warn-manuskript.txt

cd dist/manuskript

# Remove this library (causing weird bluetooth problems):
### comment: We don't need bluetooth anyway... ^^'
rm Qt5Bluetooth.dll

# Remove this library (causing a crash on Windows 7):
rm ucrtbase.dll

# Remove unnecessary libraries:
rm api-ms-win-*

# Test Manuskript:
### comment: Seems to work fine...
xvfb-run -s '-screen 0 1920x1080x24 +extension GLX' wine manuskript.exe &
WINE_TEST_PID=$!

sleep 5
cd ..

tmp_cleanup() {
	# Cleanup everything:
	### comment: removing the local git repository 
	###          requires write permissions...
	chmod +w -R $DIR/manuskript
	rm -r $DIR
}

if [ $(ps $WINE_TEST_PID | grep manuskript.exe | wc -l) -gt 0 ]; then
	kill $WINE_TEST_PID
else
	echo "ERROR: Package has crashed to an critical error!"
	tmp_cleanup
	exit
fi

ZIP_NAME=manuskript-$PKG_VERSION-$BUILD_ARCH.zip

# Package everything together:
zip -r $ZIP_NAME manuskript
mv $ZIP_NAME $EXEC_DIR

tmp_cleanup
