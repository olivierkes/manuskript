#!/usr/bin/env python
# --!-- coding: utf8 --!--

# The loadSave file calls the propper functions to load and save file
# trying to detect the proper file format if it comes from an older version
import os
import zipfile

import manuskript.load_save.version_0 as v0
import manuskript.load_save.version_1 as v1


def saveProject(version=None):

    if version == 0:
        v0.saveProject()
    else:
        v1.saveProject()


def loadProject(project):

    # Detect version
    isZip = False
    version = 0

    # Is it a zip?
    try:
        zf = zipfile.ZipFile(project)
        isZip = True
    except zipfile.BadZipFile:
        isZip = False

    # Does it have a VERSION in zip root?
    if isZip and "VERSION" in zf.namelist():
        version = int(zf.read("VERSION"))

    # Zip but no VERSION: oldest file format
    elif isZip:
        version = 0

    # Not a zip
    else:
        # Project path
        dir = os.path.dirname(project)

        # Folder containing file: name of the project file (without .msk extension)
        folder = os.path.splitext(os.path.basename(project))[0]

        # Reading VERSION file
        path = os.path.join(dir, folder, "VERSION")
        if os.path.exists(path):
            with open(path, "r") as f:
                version = int(f.read())

    print("Detected file format version:", version)

    if version == 0:
        v0.loadProject(project)
    else:
        v1.loadProject(project)
