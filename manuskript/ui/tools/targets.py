import locale

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer

from manuskript.enums import Outline
from manuskript.functions import appPath
from manuskript.ui.tools.targets_ui import Ui_targets

class targetsDialog(QWidget, Ui_targets):
    def __init__(self, parent=None, mw=None):
        QWidget.__init__(self)
        self.mw = parent
        self.setupUi(self)
        iconPic = appPath("icons/Manuskript/icon-64px.png")
        self.setWindowIcon(QIcon(iconPic))

        self.session_reset.clicked.connect(self.resetSession)
        
        self.tick()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(2000)

    def getDraftStats(self):
        item = self.mw.mdlOutline.rootItem
        wc = item.data(Outline.wordCount)
        goal = item.data(Outline.goal)
        progress = item.data(Outline.goalPercentage)
        return (wc, goal, progress)

    def resetSession(self):
        wc, _, _ = self.getDraftStats()
        self.mw.sessionStartWordCount = wc 
        self.tick()

    @staticmethod
    def progress_bar_value(value):
        return min(max(float(value) * 100, 0), 100)

    def tick(self):
        wc, goal, progress = self.getDraftStats()
        
        self.draft_wc_label.setText(locale.format("%d", wc, grouping=True))
        self.draft_goal_label.setText(locale.format("%d", goal, grouping=True))
        # limit to 0-100 for display
        self.draft_progress_bar.setValue(self.progress_bar_value(progress))  

        session_wc = wc - self.mw.sessionStartWordCount
        self.session_wc_label.setText(locale.format("%d", session_wc, grouping=True))
        if self.session_target.value() == 0:
            self.session_progress_bar.setValue(0)
        else:
            self.session_progress_bar.setValue(self.progress_bar_value(session_wc / self.session_target.value()))

    def closeEvent(self, event):
        self.timer = None
