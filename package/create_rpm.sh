#!/bin/bash
#
#        Name:  create_rpm.sh
#
# Description:  Create Fedora style RPM package for Manuskript
#
#       Usage:  create_rpm.sh [AppVersion PkgNumber]
#
#  Parameters:  Appversion - defaults to manuskript/version.py value.
#               PkgNumber  - default to 1.


#   Function to echo command and then run command
#     Usage:  echo_do eval "command-to-run"
function echo_do() {
  echo "\$ $@" | sed 's/eval //'
  "$@"
}

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
Dest="$Root/rpmbuild"

echo "### Using package directory: $Dest"

echo "### Creating folder structure"
echo_do eval "mkdir -p $Dest/{BUILD,RPMS,SOURCES,SPECS,tmp}"
echo_do eval "mkdir -p $Dest/RPMS/noarch"

echo "### Defining rpm macros"
cat <<EOF >~/.rpmmacros
%_topdir   %(echo $Dest)
%_tmppath  %{_topdir}/tmp
EOF

# Getting manuskript files, by downloading
# pushd $Dest/
# wget https://github.com/olivierkes/manuskript/archive/$AppVersion.tar.gz
# tar -xvf $AppVersion.tar.gz
# rm $AppVersion.tar.gz
# popd

# Using the current direction as source

echo "### Creating tarball folder structure"
echo_do eval "mkdir -p $Dest/$AppName-$AppVersion/{usr/share/applications,usr/bin/}"

echo "### Copying manuskript content"
echo_do eval "rsync -a --exclude=.git --include='*.msk' \
    --exclude=.github \
	--exclude-from='$Root/.gitignore' \
    --exclude=rpmbuild \
    --exclude={.codeclimate.yml,.gitignore,.travis.yml} \
    $ScriptPath/../  $Dest/$AppName-$AppVersion/usr/share/manuskript"
# Note:  Files manuskript and manuskript.desktop are same as in Debian
echo_do eval "cp $ScriptPath/create_deb/manuskript $Dest/$AppName-$AppVersion/usr/bin/manuskript"
echo_do eval "chmod 0755 $Dest/$AppName-$AppVersion/usr/bin/manuskript"
echo_do eval "cp $ScriptPath/create_deb/manuskript.desktop \
    $Dest/$AppName-$AppVersion/usr/share/applications/manuskript.desktop"

echo "### Creating SPECS/manuskript.spec file"
echo_do eval "cp $ScriptPath/create_rpm/manuskript.spec \
    $Dest/SPECS/manuskript.spec"
echo_do eval "sed -i \"s/{AppVersion}/$AppVersion/\" \
    $Dest/SPECS/manuskript.spec"
echo_do eval "sed -i \"s/{PkgNumber}/$PkgNumber/\" \
    $Dest/SPECS/manuskript.spec"

echo "### Creating tarball"
echo_do eval "tar -C $Dest -cf $Dest/SOURCES/$AppName-$AppVersion.tar.gz \
   $AppName-$AppVersion"

echo "### Removing temporary tarball directory"
echo_do eval "rm -rf $Dest/$AppName-$AppVersion"

echo "### Building the RPM package…"
echo_do eval "pushd $Dest"
echo_do eval "rpmbuild --target=noarch -bb SPECS/manuskript.spec"
echo_do eval "popd"

echo "### Done"
echo "### RPM File:  $Dest/RPMS/noarch/$AppName-$PkgVersion.noarch.rpm"
