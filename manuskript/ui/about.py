# --!-- coding: utf8 --!--

from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget
from platform import python_version

from manuskript.functions import appPath
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

        self.labelManuskriptVersion.setText(
              "<b>" + self.tr("Version") + " " + getVersion() + "</b><br>"
            + "&nbsp;"*5 + """<a href="http://www.theologeek.ch/manuskript/">
                                http://www.theologeek.ch/manuskript/
                               </a><br>"""
            + "&nbsp;"*5 + "Copyright © 2015-2017 Olivier Keshavjee<br>"
            + "&nbsp;"*5 + """<a href="https://www.gnu.org/licenses/gpl-3.0.en.html">
                                GNU General Public License Version 3
                            </a><br>"""
            )

        self.labelManuskriptVersion.setOpenExternalLinks(True)

        self.labelSoftwareVersion.setText(
              "<b>" + self.tr("Software Versions in Use:") + "</b><br>"
            + "&nbsp;"*5 + "Python " + python_version() + "<br>"
            + "&nbsp;"*5 + "PyQt " + PYQT_VERSION_STR + "<br>"
            + "&nbsp;"*5 + "Qt " + QT_VERSION_STR
            )
        #self.labelPythonVersion.setText()
        #self.labelPyQtVersion.setText()
        #self.labelQtVersion.setText()

    def accept(self):
        self.close()
