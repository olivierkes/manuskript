#!/bin/bash
set -ev
if [ z"$FILENAME" = "z" ]; then
    echo "Error:  Environment variable FILENAME is not set"
    exit 1
fi
filename="${FILENAME%.*}".dmg
export manuskript_version=$TRAVIS_BRANCH
package/osx/rebuild_mac_icon.sh
pyinstaller manuskript.spec --clean --noconfirm
# Fix signing the app - know issue with Qt5
python3 package/osx/fix_app_qt_folder_names_for_codesign.py dist/manuskript.app
codesign -s - --force --all-architectures --timestamp --deep dist/manuskript.app
# Create the installer
dmgbuild -s package/osx/dmg-settings.py "manuskript" dist/${filename}
cd dist && zip $FILENAME -r manuskript && cd ..
ls dist
cp dist/$FILENAME dist/manuskript-osx-develop.zip
cp dist/$filename dist/manuskript-osx-develop.dmg
