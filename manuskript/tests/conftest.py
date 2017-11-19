#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Fixtures."""

import pytest

@pytest.fixture(scope='session', autouse=True)
def MWEmptyProject():
    """
    Sets the mainWindow to load an empty project.
    """
    from manuskript.functions import mainWindow
    MW = mainWindow()

    import tempfile
    tf = tempfile.NamedTemporaryFile(suffix=".msk")
    MW.welcome.createFile(tf.name, overwrite=True)
    assert MW.currentProject is not None

    return MW

    # yield MW
    # # Properly destructed after. Otherwise: seg fault.
    # MW.deleteLater()
