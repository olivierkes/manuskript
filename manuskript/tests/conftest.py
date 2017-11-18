#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Fixtures."""

import pytest

@pytest.fixture(scope='session', autouse=True)
def MW():
    """
    Creates a mainWindow that can be used for the tests
    Either with functions.mainWindow or by passing argument
    MW to the test
    """
    from manuskript.mainWindow import MainWindow
    mw = MainWindow()

    yield

    # Properly destructed after. Otherwise: seg fault.
    mw.deleteLater()
