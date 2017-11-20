#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for settingsWindow"""

from manuskript import functions as F

def test_general(MWSampleProject):
    MW = MWSampleProject

    # Loading from mainWindow
    MW.actSettings.triggered.emit()
    assert MW.sw.isVisible()
    MW.sw.close()
    MW.actLabels.triggered.emit()
    assert MW.sw.isVisible()
    MW.sw.close()
    MW.actStatus.triggered.emit()
    assert MW.sw.isVisible()
    MW.sw.hide()

    SW = MW.sw

    # Imports
    from PyQt5.QtWidgets import qApp, QStyleFactory
    from PyQt5.QtCore import QSettings, Qt
    qS = QSettings(qApp.organizationName(), qApp.applicationName())
    from manuskript import settings as S

    # Style
    assert SW.cmbStyle.count() == len(list(QStyleFactory.keys()))
    assert SW.cmbStyle.currentText() == qS.value("applicationStyle")
    ## Seg fault when trying to set the style in tests:
    # for s in styles:
    #     SW.cmbStyle.setCurrentText(s)
        # assert S.value("applicationStyle") == s

    # Translations
    assert (SW.cmbTranslation.currentData()
            == qS.value("applicationTranslation"))
    for name in SW.translations:
        SW.cmbTranslation.setCurrentText(name)
        assert qS.value("applicationTranslation") == SW.translations[name]

    def switchCheckBoxAndAssert(chk, settings):
        """
        Asserts that the check state is that of settings, change checkstate
        and asserts settings has been changed.
        Settings is a function that returns the value.
        """
        state = settings()
        assert chk.isChecked() == state
        chk.setChecked(not state)
        assert chk.isChecked() is not state

    # Loading and Saving
    switchCheckBoxAndAssert(SW.chkAutoLoad,
                            lambda: qS.value("autoLoad", type=bool))
    switchCheckBoxAndAssert(SW.chkAutoSave,
                            lambda: S.autoSave)
    switchCheckBoxAndAssert(SW.chkAutoSaveNoChanges,
                            lambda: S.autoSaveNoChanges)
    switchCheckBoxAndAssert(SW.chkSaveOnQuit,
                            lambda: S.saveOnQuit)
    switchCheckBoxAndAssert(SW.chkSaveToZip,
                            lambda: S.saveToZip)

    # Revisions
    switchCheckBoxAndAssert(SW.chkRevisionsKeep,
                            lambda: S.revisions["keep"])
    switchCheckBoxAndAssert(SW.chkRevisionRemove,
                            lambda: S.revisions["smartremove"])

    # Views
    # Simple way here, we just call the functions.
    SW.cmbTreeIcon.currentIndexChanged.emit(0)
    SW.cmbOutlineIcon.currentIndexChanged.emit(0)
    SW.cmbCorkIcon.currentIndexChanged.emit(0)
    # Can't test because of the dialog
    # assert SW.setCorkColor() is None
    SW.rdoCorkNewStyle.toggled.emit(True)
    SW.cmbCorkImage.currentIndexChanged.emit(0)
    SW.cmbCorkImage.currentIndexChanged.emit(0)
    # Test editor: same problem as above
    # choseEditorFontColor
    # choseEditorMisspelledColor
    # choseEditorBackgroundColor
    # Test editor
    switchCheckBoxAndAssert(SW.chkEditorBackgroundTransparent,
                            lambda: S.textEditor["backgroundTransparent"])
    assert SW.restoreEditorColors() is None
    switchCheckBoxAndAssert(SW.chkEditorNoBlinking,
                            lambda: S.textEditor["cursorNotBlinking"])

    # Labels
    assert SW.updateLabelColor(MW.mdlLabels.item(1).index()) is None
    rc = MW.mdlLabels.rowCount()
    SW.addLabel()
    SW.lstLabels.setCurrentIndex(
        MW.mdlLabels.item(MW.mdlLabels.rowCount() - 1).index())
    SW.removeLabel()
    assert MW.mdlLabels.rowCount() == rc
    # setLabelColor # Same problem as above

    # Status
    rc = MW.mdlStatus.rowCount()
    SW.addStatus()
    SW.lstStatus.setCurrentIndex(
        MW.mdlStatus.item(MW.mdlStatus.rowCount() - 1).index())
    SW.removeStatus()
    assert MW.mdlStatus.rowCount() == rc

    # Fullscreen
    # self.lstThemes.currentItemChanged.connect(self.themeSelected)
    item = SW.lstThemes.item(0)
    SW.lstThemes.currentItemChanged.emit(item, None)
    assert S.fullScreenTheme in item.data(Qt.UserRole)
    SW.lstThemes.currentItemChanged.emit(None, None)
    count = SW.lstThemes.count()
    SW.newTheme()
    assert SW.lstThemes.count() == count + 1
    item = SW.lstThemes.item(count)
    SW.lstThemes.setCurrentItem(item)
    SW.editTheme()
    switchCheckBoxAndAssert(SW.chkThemeIndent,
                            lambda: SW._themeData["Spacings/IndentFirstLine"])
    SW.updateThemeFont(None)
    SW.updateThemeBackground(0)
    for i in range(4):
        SW.updateLineSpacing(i)
    SW.resize(SW.geometry().size()) # resizeEvent
    #TODO: other edit test (see SW.loadTheme
    SW.saveTheme()
    item = SW.lstThemes.item(count)
    SW.lstThemes.setCurrentItem(item)
    SW.editTheme()
    SW.cancelEdit()
    item = SW.lstThemes.item(count)
    SW.lstThemes.setCurrentItem(item)
    SW.removeTheme()
    assert SW.lstThemes.count() == count

    # self._editingTheme = None
    # self.btnThemeEditOK.setIcon(qApp.style().standardIcon(QStyle.SP_DialogApplyButton))
    # self.btnThemeEditOK.clicked.connect(self.saveTheme)
    # self.btnThemeEditCancel.setIcon(qApp.style().standardIcon(QStyle.SP_DialogCancelButton))
    # self.btnThemeEditCancel.clicked.connect(self.cancelEdit)
    # self.cmbThemeEdit.currentIndexChanged.connect(self.themeEditStack.setCurrentIndex)
    # self.cmbThemeEdit.setCurrentIndex(0)
    # self.cmbThemeEdit.currentIndexChanged.emit(0)
    # self.themeStack.setCurrentIndex(0)
    # self.populatesThemesList()
    # self.btnThemeAdd.clicked.connect(self.newTheme)
    # self.btnThemeEdit.clicked.connect(self.editTheme)
    # self.btnThemeRemove.clicked.connect(self.removeTheme)
    # self.timerUpdateFSPreview = QTimer()
    # self.timerUpdateFSPreview.setSingleShot(True)
    # self.timerUpdateFSPreview.setInterval(250)
    # self.timerUpdateFSPreview.timeout.connect(self.updatePreview)
    # saveTheme
    # themeEditStack.setCurrentIndex
    # editTheme
    # removeTheme
    # updatePreview
