#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for settingsWindow"""

def test_loadImportWiget(MWSampleProject):
    """
    Simply tests that import widget loads properly.
    """
    MW = MWSampleProject

    # Loading from mainWindow
    MW.doImport()
    I = MW.dialog
    assert I.isVisible()
    I.hide()
    I.close()

#FIXME: test significant stuff
