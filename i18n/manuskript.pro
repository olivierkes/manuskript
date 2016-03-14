FORMS            += ../manuskript/ui/mainWindow.ui
FORMS            += ../manuskript/ui/settings_ui.ui
FORMS            += ../manuskript/ui/welcome_ui.ui
FORMS            += ../manuskript/ui/sldImportance_ui.ui
FORMS            += ../manuskript/ui/cheatSheet_ui.ui
FORMS            += ../manuskript/ui/compileDialog_ui.ui
FORMS            += ../manuskript/ui/revisions_ui.ui

FORMS            += ../manuskript/ui/editors/editorWidget_ui.ui
FORMS            += ../manuskript/ui/editors/locker_ui.ui

FORMS            += ../manuskript/ui/views/propertiesView_ui.ui
FORMS            += ../manuskript/ui/views/basicItemView_ui.ui
FORMS            += ../manuskript/ui/views/metadataView_ui.ui

SOURCES          += ../manuskript/main.py
SOURCES          += ../manuskript/loadSave.py
SOURCES          += ../manuskript/mainWindow.py
SOURCES          += ../manuskript/settingsWindow.py

SOURCES          += ../manuskript/models/outlineModel.py
SOURCES          += ../manuskript/models/persosProxyModel.py
SOURCES          += ../manuskript/models/plotModel.py
SOURCES          += ../manuskript/models/worldModel.py
SOURCES          += ../manuskript/models/persosModel.py
SOURCES          += ../manuskript/models/references.py

SOURCES          += ../manuskript/exporter/__init__.py

SOURCES          += ../manuskript/ui/helpLabel.py
SOURCES          += ../manuskript/ui/sldImportance.py
SOURCES          += ../manuskript/ui/welcome.py
SOURCES          += ../manuskript/ui/cheatSheet.py
SOURCES          += ../manuskript/ui/compileDialog.py
SOURCES          += ../manuskript/ui/revisions.py
SOURCES          += ../manuskript/ui/collapsibleDockWidgets.py

SOURCES          += ../manuskript/ui/editors/editorWidget.py
SOURCES          += ../manuskript/ui/editors/fullScreenEditor.py
SOURCES          += ../manuskript/ui/editors/locker.py
SOURCES          += ../manuskript/ui/editors/textFormat.py
SOURCES          += ../manuskript/ui/editors/completer.py
SOURCES          += ../manuskript/ui/editors/mainEditor.py

SOURCES          += ../manuskript/ui/views/corkDelegate.py
SOURCES          += ../manuskript/ui/views/outlineDelegates.py
SOURCES          += ../manuskript/ui/views/outlineBasics.py
SOURCES          += ../manuskript/ui/views/cmbOutlineLabelChoser.py
SOURCES          += ../manuskript/ui/views/cmbOutlinePersoChoser.py
SOURCES          += ../manuskript/ui/views/cmbOutlineStatusChoser.py
SOURCES          += ../manuskript/ui/views/treeView.py
SOURCES          += ../manuskript/ui/views/lineEditView.py
SOURCES          += ../manuskript/ui/views/textEditView.py
SOURCES          += ../manuskript/ui/views/plotTreeView.py
SOURCES          += ../manuskript/ui/views/plotDelegate.py

TRANSLATIONS     += manuskript_fr.ts
TRANSLATIONS     += manuskript_es.ts
