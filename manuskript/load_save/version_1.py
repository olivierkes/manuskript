#!/usr/bin/env python
# --!-- coding: utf8 --!--

# Version 1 of file saving format.
# Aims at providing a plain-text way of saving a project
# (except for some elements), allowing collaborative work
# versioning and third-partty editing.
import os
import zipfile

from manuskript import settings
from manuskript.functions import mainWindow

try:
    import zlib  # Used with zipfile for compression

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED


def saveProject(zip=None):
    """
    Saves the project. If zip is False, the project is saved as a multitude of plain-text files for the most parts
    and some XML or zip? for settings and stuff.
    If zip is True, everything is saved as a single zipped file. Easier to carry around, but does not allow
    collaborative work, versionning, or third-party editing.
    @param zip: if True, saves as a single file. If False, saves as plain-text. If None, tries to determine based on
    settings.
    @return: Nothing
    """
    if zip is None:
        zip = False
        # Fixme


    files = []
    mw = mainWindow()

    # files.append((saveStandardItemModelXML(mw.mdlFlatData),
    #               "flatModel.xml"))
    # # files.append((saveStandardItemModelXML(self.mdlCharacter),
    # #               "perso.xml"))
    # files.append((saveStandardItemModelXML(mw.mdlWorld),
    #               "world.xml"))
    # files.append((saveStandardItemModelXML(mw.mdlLabels),
    #               "labels.xml"))
    # files.append((saveStandardItemModelXML(mw.mdlStatus),
    #               "status.xml"))
    # files.append((saveStandardItemModelXML(mw.mdlPlots),
    #               "plots.xml"))
    # files.append((mw.mdlOutline.saveToXML(),
    #               "outline.xml"))
    # files.append((settings.save(),
    #               "settings.pickle"))

    files.append(("blabla", "test/machin.txt"))
    files.append(("youpi", "encore/truc.txt"))

    project = mw.currentProject

    project = os.path.join(
        os.path.dirname(project),
        "_" + os.path.basename(project)
    )

    zf = zipfile.ZipFile(project, mode="w")

    for content, filename in files:
        zf.writestr(filename, content, compress_type=compression)

    zf.close()


def loadProject(project):
    """
    Loads a project.
    @param project: the filename of the project to open.
    @return: an array of errors, empty if None.
    """
    pass