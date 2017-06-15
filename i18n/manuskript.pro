FORMS            += ../manuskript/ui/revisions_ui.ui
FORMS            += ../manuskript/ui/mainWindow.ui
FORMS            += ../manuskript/ui/search_ui.ui
FORMS            += ../manuskript/ui/tools/frequency_ui.ui
FORMS            += ../manuskript/ui/welcome_ui.ui
FORMS            += ../manuskript/ui/cheatSheet_ui.ui
FORMS            += ../manuskript/ui/settings_ui.ui

FORMS            += ../manuskript/ui/editors/editorWidget_ui.ui
FORMS            += ../manuskript/ui/editors/textFormat_ui.ui
FORMS            += ../manuskript/ui/editors/locker_ui.ui
FORMS            += ../manuskript/ui/editors/completer_ui.ui
FORMS            += ../manuskript/ui/editors/mainEditor_ui.ui
FORMS            += ../manuskript/ui/editors/tabSplitter_ui.ui

FORMS            += ../manuskript/ui/views/propertiesView_ui.ui
FORMS            += ../manuskript/ui/views/metadataView_ui.ui
FORMS            += ../manuskript/ui/views/basicItemView_ui.ui
FORMS            += ../manuskript/ui/views/sldImportance_ui.ui
FORMS            += ../manuskript/ui/views/storylineView_ui.ui

FORMS            += ../manuskript/ui/exporters/exporter_ui.ui
FORMS            += ../manuskript/ui/exporters/exportersManager_ui.ui
FORMS            += ../manuskript/ui/exporters/manuskript/plainTextSettings_ui.ui


SOURCES          += ../manuskript/exporter/__init__.py
SOURCES          += ../manuskript/load_save/version_0.py
SOURCES          += ../manuskript/main.py
SOURCES          += ../manuskript/mainWindow.py
SOURCES          += ../manuskript/models/characterModel.py
SOURCES          += ../manuskript/models/outlineModel.py
SOURCES          += ../manuskript/models/persosProxyModel.py
SOURCES          += ../manuskript/models/plotModel.py
SOURCES          += ../manuskript/models/plotsProxyModel.py
SOURCES          += ../manuskript/models/references.py
SOURCES          += ../manuskript/models/worldModel.py
SOURCES          += ../manuskript/settingsWindow.py
SOURCES          += ../manuskript/ui/cheatSheet.py
SOURCES          += ../manuskript/ui/collapsibleDockWidgets.py
SOURCES          += ../manuskript/ui/editors/fullScreenEditor.py
SOURCES          += ../manuskript/ui/editors/locker.py
SOURCES          += ../manuskript/ui/editors/mainEditor.py
SOURCES          += ../manuskript/ui/editors/textFormat.py
SOURCES          += ../manuskript/ui/editors/tabSplitter.py
SOURCES          += ../manuskript/ui/helpLabel.py
SOURCES          += ../manuskript/ui/revisions.py
SOURCES          += ../manuskript/ui/search.py
SOURCES          += ../manuskript/ui/tools/frequencyAnalyzer.py
SOURCES          += ../manuskript/ui/views/characterTreeView.py
SOURCES          += ../manuskript/ui/views/cmbOutlineCharacterChoser.py
SOURCES          += ../manuskript/ui/views/cmbOutlineLabelChoser.py
SOURCES          += ../manuskript/ui/views/cmbOutlineStatusChoser.py
SOURCES          += ../manuskript/ui/views/corkDelegate.py
SOURCES          += ../manuskript/ui/views/lineEditView.py
SOURCES          += ../manuskript/ui/views/outlineBasics.py
SOURCES          += ../manuskript/ui/views/outlineDelegates.py
SOURCES          += ../manuskript/ui/views/plotDelegate.py
SOURCES          += ../manuskript/ui/views/plotTreeView.py
SOURCES          += ../manuskript/ui/views/sldImportance.py
SOURCES          += ../manuskript/ui/views/storylineView.py
SOURCES          += ../manuskript/ui/views/textEditCompleter.py
SOURCES          += ../manuskript/ui/views/textEditView.py
SOURCES          += ../manuskript/ui/views/treeView.py
SOURCES          += ../manuskript/ui/welcome.py
SOURCES          += ../manuskript/ui/exporters/exporter.py
SOURCES          += ../manuskript/ui/exporters/exportersManager.py
SOURCES          += ../manuskript/ui/exporters/manuskript/plainTextSettings.py


SOURCES          += ../manuskript/exporter/basic.py
SOURCES          += ../manuskript/exporter/mmd.py
SOURCES          += ../manuskript/exporter/manuskript/__init__.py
SOURCES          += ../manuskript/exporter/manuskript/HTML.py
SOURCES          += ../manuskript/exporter/manuskript/markdown.py
SOURCES          += ../manuskript/exporter/manuskript/plainText.py

SOURCES          +=../manuskript/exporter/pandoc/HTML.py
SOURCES          +=../manuskript/exporter/pandoc/__init__.py
SOURCES          +=../manuskript/exporter/pandoc/outputFormats.py
SOURCES          +=../manuskript/exporter/pandoc/PDF.py
SOURCES          +=../manuskript/exporter/pandoc/plainText.py
SOURCES          +=../manuskript/exporter/pandoc/abstractPlainText.py

TRANSLATIONS     += manuskript_fr.ts
TRANSLATIONS     += manuskript_es.ts
TRANSLATIONS     += manuskript_de.ts
