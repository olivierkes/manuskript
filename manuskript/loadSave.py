#!/usr/bin/env python
# --!-- coding: utf8 --!--

# The loadSave file calls the propper functions to load and save file
# trying to detect the proper file format if it comes from an older version

import manuskript.load_save.version_0 as v0
import manuskript.load_save.version_1 as v1

def saveProject(version=None):

    if version == 0:
        v0.saveProject()
    else:
        v1.saveProject()


def loadProject(project):

    # Detect version
    # FIXME
    version = 0

    if version == 0:
        v0.loadProject(project)
    else:
        v1.loadProject(project)
