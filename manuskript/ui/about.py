# --!-- coding: utf8 --!--

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget
from platform import python_version

from manuskript.functions import appPath
from manuskript.ui import about
from manuskript.ui.about_ui import Ui_about
from manuskript.version import getVersion

class aboutDialog(QWidget, Ui_about):
    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.populateFields()
        self.buttonBox.accepted.connect(self.accept)

    def populateFields(self):
        # Fill in all the fields in the About dialog
        iconPic = appPath("icons/Manuskript/icon-64px.png")
        self.setWindowIcon(QIcon(iconPic))

        logoPic = QPixmap(appPath("icons/Manuskript/logo-400x104.png"))
        self.labelLogo.setPixmap(logoPic)

        self.labelManuskriptVersion.setText(self.tr("Version") + " " + getVersion())

        self.labelWebsite.setText(
               "<a href=\"http://www.theologeek.ch/manuskript/\">" \
             + "http://www.theologeek.ch/manuskript/" \
             + "</a>" )
        self.labelWebsite.setOpenExternalLinks(True)

        self.labelLicense.setText( \
               "<a href=\"https://www.gnu.org/licenses/gpl-3.0.en.html\">" \
             + self.tr("GNU General Public License Version 3") \
             + "</a>" )
        self.labelLicense.setOpenExternalLinks(True)

        self.labelPythonVersion.setText(self.tr("Python") + " " + python_version())
        self.labelPyQtVersion.setText(self.tr("PyQt") + " " + PYQT_VERSION_STR)
        self.labelQtVersion.setText(self.tr("Qt") + " " + QT_VERSION_STR)

    def accept(self):
        self.close()
