import os

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope='session')
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


@pytest.fixture
def editor(qapp):
    from manuskript.ui.views.MDEditView import MDEditView
    ed = MDEditView()
    ed.setEnabled(True)
    ed.enableVim()
    return ed
