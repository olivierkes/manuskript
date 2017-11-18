#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests."""

import pytest

# We need a qApplication to be running, or all the calls to qApp
# will throw a seg fault.
from PyQt5.QtWidgets import QApplication
app = QApplication([])

@pytest.yield_fixture(scope='session', autouse=True)
def MW():

    # Creates a mainWindow that can be used for the tests
    # Either with functions.mainWindow or by passing argument
    # MW to the test
    from manuskript.mainWindow import MainWindow
    mw = MainWindow()

    yield

    # Properly destructed after. Otherwise: seg fault.
    mw.deleteLater()
