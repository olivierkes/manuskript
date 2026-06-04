#!/bin/bash
set -ev

# Program vars
ScriptPath="$( cd "$(dirname "$0")" ; pwd -P )"
Root="$ScriptPath/../"

# Manuskript Vars
AppName=manuskript
Version=$(grep -E  "__version__.*\".*\"" "$Root/manuskript/version.py" \
          | cut -d\" -f2)  # Look for version in manuskript/version
AppVersion=${1:-$Version}
echo "Using GIT_SHA_SHORT: $GIT_SHA_SHORT"
PkgNumber=${2:-${GIT_SHA_SHORT:-2}}
PkgName=$AppName-$AppVersion-$PkgNumber

package/osx/rebuild_mac_icon.sh
pyinstaller manuskript.spec --clean --noconfirm
# Fix signing the app - know issue with Qt5
python3 package/osx/fix_app_qt_folder_names_for_codesign.py dist/manuskript.app
codesign -s - --force --all-architectures --timestamp --deep dist/manuskript.app
# Create the installer
dmgbuild -s package/osx/dmg-settings.py "manuskript" dist/${PkgName}.dmg
cd dist && zip ${PkgName}.zip manuskript && cd ..
