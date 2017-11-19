#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Fixtures."""

import pytest

# @pytest.fixture(scope='session', autouse=True)
# def MW():
#     """
#     Creates a mainWindow that can be used for the tests
#     Either with functions.mainWindow or by passing argument
#     MW to the test
#     """
#     from manuskript.mainWindow import MainWindow
#     mw = MainWindow()
#
#     yield
#
#     # Properly destructed after. Otherwise: seg fault.
#     mw.deleteLater()

@pytest.fixture
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
