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
    MW.sw.setTab("General")

    SW = MW.sw

    # Imports
    from PyQt5.QtWidgets import qApp, QStyleFactory
    from PyQt5.QtCore import QSettings, Qt
    qS = QSettings(qApp.organizationName(), qApp.applicationName())
    from manuskript import settings as S

    # Style
    assert SW.cmbStyle.count() == len(list(QStyleFactory.keys()))
    if qS.value("applicationStyle"):
        assert SW.cmbStyle.currentText() == qS.value("applicationStyle")
    ## Seg fault when trying to set the style in tests:
    # for s in styles:
    #     SW.cmbStyle.setCurrentText(s)
        # assert S.value("applicationStyle") == s

    # Translations
    if qS.value("applicationTranslation"):
        assert (SW.cmbTranslation.currentData()
                == qS.value("applicationTranslation"))
    for name in SW.translations:
        SW.cmbTranslation.setCurrentText(name)
        if qS.value("applicationTranslation"):
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
    SW.txtAutoSave.setText("0")
    SW.txtAutoSaveNoChanges.setText("0")
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
    SW.chkOutlineTitle.setChecked(Qt.Checked)  #outlineColumnsChanged
    SW.chkOutlineTitle.setChecked(Qt.Unchecked)
    SW.chkOutlineTitle.setChecked(Qt.Checked)
    # Can't test because of the dialog
    # assert SW.setCorkColor() is None
    SW.sldTreeIconSize.setValue(SW.sldTreeIconSize.value() + 1)
    SW.rdoCorkNewStyle.toggled.emit(True)
    SW.cmbCorkImage.currentIndexChanged.emit(0)
    SW.cmbCorkImage.currentIndexChanged.emit(1)
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
    # Twice on purpose: set and restore
    switchCheckBoxAndAssert(SW.chkEditorNoBlinking,
                            lambda: S.textEditor["cursorNotBlinking"])
    # Manually call updateAllWidgets, because other wise timer of 250ms
    SW.updateAllWidgets()

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
    SW.newTheme() # theme with same name
    item = SW.lstThemes.item(SW.lstThemes.count() - 1)
    SW.lstThemes.setCurrentItem(item)
    SW.removeTheme()
    item = SW.lstThemes.item(count)
    SW.lstThemes.setCurrentItem(item)
    SW.editTheme()
    switchCheckBoxAndAssert(SW.chkThemeIndent,
                            lambda: SW._themeData["Spacings/IndentFirstLine"])
    SW.updateThemeFont(None)
    SW.updateThemeBackground(0)
    SW.updateThemeBackground(1)
    SW.spnThemeLineSpacing.setValue(123)
    for i in range(4):
        SW.updateLineSpacing(i)
        SW.updateUIFromTheme() # No time to wait on timer
    assert SW._editingTheme is not None
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
