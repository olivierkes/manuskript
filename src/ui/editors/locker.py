#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from ui.editors.locker_ui import Ui_locker
from functions import *
import models.references as Ref

class locker(QWidget, Ui_locker):
    
    locked = pyqtSignal()
    unlocked = pyqtSignal()
    lockChanged = pyqtSignal(bool)
    
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._btnText = None
        self._words = None
        self._target = None
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.unlock)
        self.timer.stop()
        self.timerSec = QTimer(self)
        self.timerSec.setInterval(500)
        self.timerSec.timeout.connect(self.updateBtnText)
        self.timerSec.stop()
        self.rbtnWordTarget.toggled.connect(self.spnWordTarget.setVisible)
        self.rbtnTimeTarget.toggled.connect(self.spnTimeTarget.setVisible)
        self.rbtnWordTarget.setChecked(True)
        self.spnTimeTarget.setVisible(False)
        
        self.btnLock.clicked.connect(self.lock)
        
    def lock(self):
        if self.rbtnWordTarget.isChecked():
            self._target = self._words + self.spnWordTarget.value()
            
        elif self.rbtnTimeTarget.isChecked():
            self.timer.setInterval(self.spnTimeTarget.value() * 1000 * 60)
            self.timer.start()
            self.timerSec.start()
            self.updateBtnText()
            
        self.setEnabled(False)
        self.locked.emit()
        self.lockChanged.emit(True)
        
    def unlock(self):
        self.setEnabled(True)
        self.btnLock.setText(self._btnText)
        self.timer.stop()
        self.timerSec.stop()
        self._target = None
        self.unlocked.emit()
        self.lockChanged.emit(False)
        
    def isLocked(self):
        return not self.isEnabled()
        
    def setWordCount(self, wc):
        self._words = wc
        if self.isLocked():
            self.updateBtnText()
            if self._words >= self._target:
                self.unlock()
        
    def updateBtnText(self):
        if not self._btnText:
            self._btnText = self.btnLock.text()
            
        # Time locked
        if self.timer.remainingTime() != -1:
            t = self.timer.remainingTime()
            t = int(t / 1000)
            if t > 60 * 60:
                text = self.tr("~{} h.").format(str(int(t / 60 / 60)))
            elif t > 60 * 5:
                text = self.tr("~{} mn.").format(str(int(t / 60)))
            elif t > 60:
                mn = int(t / 60)
                sec = t - 60 * mn
                text = self.tr("{}:{}").format(str(mn), str(sec))
            else:
                text = self.tr("{} s.").format(str(t))
                
            self.btnLock.setText(self.tr("{} remaining").format(
                text))
        
        # Word locked
        elif self._target != None:
            self.btnLock.setText(self.tr("{} words remaining").format(
                self._target - self._words))
            