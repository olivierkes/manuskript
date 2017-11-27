#!/bin/bash

# Can take two parameters: AppVersion PkgNumber
# If not provided, AppVersion is found in manuskript/version.py
# PkgNumber is 1.

# Program vars
ScriptPath="$( cd "$(dirname "$0")" ; pwd -P )"
Root="$ScriptPath/../"

# Manuskript Vars
AppName=manuskript
Version=$(grep -E  "__version__.*\".*\"" "$Root/manuskript/version.py" \
          | cut -d\" -f2)  # Look for version in manuskript/version
AppVersion=${1:-$Version}
PkgNumber=${2:-1}
PkgVersion=$AppVersion-$PkgNumber
Dest="$Root/dist/$AppName-$PkgVersion"

echo "Package directory: $Dest"

echo -n "Creating folder structure"
mkdir -p "$Dest/DEBIAN"
mkdir -p "$Dest/usr/bin"
mkdir -p "$Dest/usr/share/applications"
echo " [✓]"

# Getting manuskript files, by downloading
# pushd $Dest/usr/share
# wget https://github.com/olivierkes/manuskript/archive/$AppVersion.tar.gz
# tar -xvf $AppVersion.tar.gz
# rm $AppVersion.tar.gz
# mv manuskript-0.5.0 manuskript
# popd

# Using the current direction as source

echo -n "Copying manuskript content"
rsync -a --exclude=.git --include="*.msk" --exclude-from="$Root/.gitignore" \
      "$ScriptPath/../"  "$Dest/usr/share/manuskript"
cp "$ScriptPath/create_deb/manuskript" "$Dest/usr/bin/manuskript"
cp "$ScriptPath/create_deb/manuskript.desktop" \
   "$Dest/usr/share/applications/manuskript.desktop"
cp "$ScriptPath/create_deb/control" "$Dest/DEBIAN/control"

sed -i "s/{PkgVersion}/$PkgVersion/" "$Dest/DEBIAN/control"
PkgSizeInKb=$(du -sk "$Dest" | cut -f 1)
sed -i "s/{PkgSizeInKb}/$PkgSizeInKb/" "$Dest/DEBIAN/control"
echo " [✓]"

echo -n "Setting permissions"
chmod 0755 "$Dest/usr/bin/manuskript"
echo " [✓]"

echo "Your root password might now be asked to finish setting permissions:"
sudo chown root:root -R "$Dest"

echo "Creating the package…"
dpkg -b "$Dest"

echo -n "Removing build folder"
sudo rm -r "$Dest"
echo " [✓]"

echo Done !
