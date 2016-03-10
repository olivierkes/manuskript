#!/usr/bin/env python
# --!-- coding: utf8 --!--

# The loadSave file calls the propper functions to load and save file
# trying to detect the proper file format if it comes from an older version
import os
import zipfile

import manuskript.load_save.version_0 as v0
import manuskript.load_save.version_1 as v1


def saveProject(version=None):

    # While debugging, we don't save the project
    # return

    if version == 0:
        v0.saveProject()
    else:
        v1.saveProject()

    # FIXME: add settings to chose between saving as zip or not.


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
        with open(project, "r") as f:
            version = int(f.read())

    print("Loading:", project)
    print("Detected file format version:", version)

    if version == 0:
        v0.loadProject(project)
    else:
        v1.loadProject(project, zip=isZip)
