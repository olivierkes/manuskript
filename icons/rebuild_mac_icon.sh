#!/bin/sh


# Build macOS specific icon set

ICON_FOLDER=./Manuskript
FULLSIZE_ICON=$ICON_FOLDER/icon-512px.png
TMP_ICONSET_FOLDER=$ICON_FOLDER/Manuskript.iconset
TARGET_ICONSET=$ICON_FOLDER/Manuskript.icns
mkdir $TMP_ICONSET_FOLDER
sips -z 16 16     $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_16x16.png
sips -z 32 32     $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_16x16@2x.png
sips -z 32 32     $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_32x32.png
sips -z 64 64     $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_32x32@2x.png
sips -z 128 128   $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_128x128.png
sips -z 256 256   $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_128x128@2x.png
sips -z 256 256   $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_256x256.png
sips -z 512 512   $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_256x256@2x.png
sips -z 512 512   $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_512x512.png
sips -z 1024 1024 $FULLSIZE_ICON --out $TMP_ICONSET_FOLDER/icon_512x512@2x.png
iconutil -c icns --output $TARGET_ICONSET $TMP_ICONSET_FOLDER
rm -R $TMP_ICONSET_FOLDER
