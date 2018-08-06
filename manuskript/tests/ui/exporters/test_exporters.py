#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for settingsWindow"""

def test_loadExportWiget(MWSampleProject):
    """
    Simply tests that export widget loads properly.
    """
    MW = MWSampleProject

    # Loading from mainWindow
    MW.doCompile()
    E = MW.dialog
    assert E.isVisible()
    E.hide()

    # Load exporter manager
    E.openManager()
    EM = E.dialog
    assert EM.isVisible()
    EM.hide()

    EM.close()
    E.close()

#FIXME: test significant stuff
