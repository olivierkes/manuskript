FORMS += ../manuskript/ui/exporters/exporter_ui.ui
FORMS += ../manuskript/ui/exporters/manuskript/plainTextSettings_ui.ui
FORMS += ../manuskript/ui/exporters/exportersManager_ui.ui
FORMS += ../manuskript/ui/about_ui.ui
FORMS += ../manuskript/ui/welcome_ui.ui
FORMS += ../manuskript/ui/mainWindow.ui
FORMS += ../manuskript/ui/importers/generalSettings_ui.ui
FORMS += ../manuskript/ui/importers/importer_ui.ui
FORMS += ../manuskript/ui/search_ui.ui
FORMS += ../manuskript/ui/settings_ui.ui
FORMS += ../manuskript/ui/tools/frequency_ui.ui
FORMS += ../manuskript/ui/tools/targets_ui.ui
FORMS += ../manuskript/ui/editors/locker_ui.ui
FORMS += ../manuskript/ui/editors/editorWidget_ui.ui
FORMS += ../manuskript/ui/editors/completer_ui.ui
FORMS += ../manuskript/ui/editors/textFormat_ui.ui
FORMS += ../manuskript/ui/editors/mainEditor_ui.ui
FORMS += ../manuskript/ui/editors/tabSplitter_ui.ui
FORMS += ../manuskript/ui/cheatSheet_ui.ui
FORMS += ../manuskript/ui/revisions_ui.ui
FORMS += ../manuskript/ui/views/storylineView_ui.ui
FORMS += ../manuskript/ui/views/sldImportance_ui.ui
FORMS += ../manuskript/ui/views/basicItemView_ui.ui
FORMS += ../manuskript/ui/views/propertiesView_ui.ui
FORMS += ../manuskript/ui/views/metadataView_ui.ui
FORMS += ../manuskript/ui/listDialog_ui.ui
SOURCES += ../manuskript/functions/__init__.py
SOURCES += ../manuskript/functions/spellchecker.py
SOURCES += ../manuskript/__init__.py
SOURCES += ../manuskript/enums.py
SOURCES += ../manuskript/converters/__init__.py
SOURCES += ../manuskript/converters/abstractConverter.py
SOURCES += ../manuskript/converters/pandocConverter.py
SOURCES += ../manuskript/converters/markdownConverter.py
SOURCES += ../manuskript/main.py
SOURCES += ../manuskript/mainWindow.py
SOURCES += ../manuskript/logging.py
SOURCES += ../manuskript/exporter/__init__.py
SOURCES += ../manuskript/exporter/basic.py
SOURCES += ../manuskript/exporter/pandoc/__init__.py
SOURCES += ../manuskript/exporter/pandoc/abstractOutput.py
SOURCES += ../manuskript/exporter/pandoc/outputFormats.py
SOURCES += ../manuskript/exporter/pandoc/abstractPlainText.py
SOURCES += ../manuskript/exporter/pandoc/HTML.py
SOURCES += ../manuskript/exporter/pandoc/PDF.py
SOURCES += ../manuskript/exporter/pandoc/plainText.py
SOURCES += ../manuskript/exporter/manuskript/__init__.py
SOURCES += ../manuskript/exporter/manuskript/markdown.py
SOURCES += ../manuskript/exporter/manuskript/HTML.py
SOURCES += ../manuskript/exporter/manuskript/plainText.py
SOURCES += ../manuskript/tests/__init__.py
SOURCES += ../manuskript/tests/load_save/__init__.py
SOURCES += ../manuskript/tests/load_save/test_ParseMMDFile.py
SOURCES += ../manuskript/tests/models/__init__.py
SOURCES += ../manuskript/tests/models/test_searchFilter.py
SOURCES += ../manuskript/tests/models/test_searchResultModel.py
SOURCES += ../manuskript/tests/models/test_outlineItem.py
SOURCES += ../manuskript/tests/models/test_references.py
SOURCES += ../manuskript/tests/models/conftest.py
SOURCES += ../manuskript/tests/test_settingsWindow.py
SOURCES += ../manuskript/tests/ui/exporters/__init__.py
SOURCES += ../manuskript/tests/ui/exporters/test_exporters.py
SOURCES += ../manuskript/tests/ui/__init__.py
SOURCES += ../manuskript/tests/ui/importers/__init__.py
SOURCES += ../manuskript/tests/ui/importers/test_importers.py
SOURCES += ../manuskript/tests/ui/test_welcome.py
SOURCES += ../manuskript/tests/ui/test_searchMenu.py
SOURCES += ../manuskript/tests/conftest.py
SOURCES += ../manuskript/tests/test_functions.py
SOURCES += ../manuskript/searchLabels.py
SOURCES += ../manuskript/settings.py
SOURCES += ../manuskript/importer/__init__.py
SOURCES += ../manuskript/importer/pandocImporters.py
SOURCES += ../manuskript/importer/mindMapImporter.py
SOURCES += ../manuskript/importer/markdownImporter.py
SOURCES += ../manuskript/importer/folderImporter.py
SOURCES += ../manuskript/importer/opmlImporter.py
SOURCES += ../manuskript/importer/abstractImporter.py
SOURCES += ../manuskript/load_save/__init__.py
SOURCES += ../manuskript/load_save/version_1.py
SOURCES += ../manuskript/load_save/version_0.py
SOURCES += ../manuskript/loadSave.py
SOURCES += ../manuskript/models/__init__.py
SOURCES += ../manuskript/models/searchResultModel.py
SOURCES += ../manuskript/models/outlineItem.py
SOURCES += ../manuskript/models/searchableItem.py
SOURCES += ../manuskript/models/plotsProxyModel.py
SOURCES += ../manuskript/models/worldModel.py
SOURCES += ../manuskript/models/persosProxyModel.py
SOURCES += ../manuskript/models/characterPOVModel.py
SOURCES += ../manuskript/models/abstractItem.py
SOURCES += ../manuskript/models/plotModel.py
SOURCES += ../manuskript/models/searchFilter.py
SOURCES += ../manuskript/models/references.py
SOURCES += ../manuskript/models/outlineModel.py
SOURCES += ../manuskript/models/flatDataModelWrapper.py
SOURCES += ../manuskript/models/abstractModel.py
SOURCES += ../manuskript/models/searchableModel.py
SOURCES += ../manuskript/models/characterModel.py
SOURCES += ../manuskript/version.py
SOURCES += ../manuskript/ui/exporters/__init__.py
SOURCES += ../manuskript/ui/exporters/exportersManager_ui.py
SOURCES += ../manuskript/ui/exporters/manuskript/__init__.py
SOURCES += ../manuskript/ui/exporters/manuskript/plainTextSettings.py
SOURCES += ../manuskript/ui/exporters/manuskript/plainTextSettings_ui.py
SOURCES += ../manuskript/ui/exporters/exporter.py
SOURCES += ../manuskript/ui/exporters/exportersManager.py
SOURCES += ../manuskript/ui/exporters/exporter_ui.py
SOURCES += ../manuskript/ui/__init__.py
SOURCES += ../manuskript/ui/listDialog.py
SOURCES += ../manuskript/ui/mainWindow.py
SOURCES += ../manuskript/ui/revisions_ui.py
SOURCES += ../manuskript/ui/about_ui.py
SOURCES += ../manuskript/ui/importers/__init__.py
SOURCES += ../manuskript/ui/importers/generalSettings_ui.py
SOURCES += ../manuskript/ui/importers/importer_ui.py
SOURCES += ../manuskript/ui/importers/importer.py
SOURCES += ../manuskript/ui/importers/generalSettings.py
SOURCES += ../manuskript/ui/highlighters/basicHighlighter.py
SOURCES += ../manuskript/ui/highlighters/__init__.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/abstractSpecificSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/__init__.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/worldSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/plotSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/characterSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/abstractSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/plotStepSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/outlineSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/searchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/flatDataSearchResultHighlighter.py
SOURCES += ../manuskript/ui/highlighters/searchResultHighlighters/widgetSelectionHighlighter.py
SOURCES += ../manuskript/ui/highlighters/MMDHighlighter.py
SOURCES += ../manuskript/ui/highlighters/markdownTokenizer.py
SOURCES += ../manuskript/ui/highlighters/markdownHighlighter.py
SOURCES += ../manuskript/ui/highlighters/markdownEnums.py
SOURCES += ../manuskript/ui/tools/__init__.py
SOURCES += ../manuskript/ui/tools/splitDialog.py
SOURCES += ../manuskript/ui/tools/frequency_ui.py
SOURCES += ../manuskript/ui/tools/targets_ui.py
SOURCES += ../manuskript/ui/tools/frequencyAnalyzer.py
SOURCES += ../manuskript/ui/tools/targets.py
SOURCES += ../manuskript/ui/helpLabel.py
SOURCES += ../manuskript/ui/editors/completer_ui.py
SOURCES += ../manuskript/ui/editors/fullScreenEditor.py
SOURCES += ../manuskript/ui/editors/__init__.py
SOURCES += ../manuskript/ui/editors/blockUserData.py
SOURCES += ../manuskript/ui/editors/textFormat.py
SOURCES += ../manuskript/ui/editors/MDFunctions.py
SOURCES += ../manuskript/ui/editors/locker.py
SOURCES += ../manuskript/ui/editors/locker_ui.py
SOURCES += ../manuskript/ui/editors/editorWidget.py
SOURCES += ../manuskript/ui/editors/completer.py
SOURCES += ../manuskript/ui/editors/textFormat_ui.py
SOURCES += ../manuskript/ui/editors/tabSplitter.py
SOURCES += ../manuskript/ui/editors/themes.py
SOURCES += ../manuskript/ui/editors/tabSplitter_ui.py
SOURCES += ../manuskript/ui/editors/mainEditor.py
SOURCES += ../manuskript/ui/editors/editorWidget_ui.py
SOURCES += ../manuskript/ui/editors/mainEditor_ui.py
SOURCES += ../manuskript/ui/revisions.py
SOURCES += ../manuskript/ui/search_ui.py
SOURCES += ../manuskript/ui/style.py
SOURCES += ../manuskript/ui/cheatSheet_ui.py
SOURCES += ../manuskript/ui/views/outlineView.py
SOURCES += ../manuskript/ui/views/corkView.py
SOURCES += ../manuskript/ui/views/metadataView_ui.py
SOURCES += ../manuskript/ui/views/__init__.py
SOURCES += ../manuskript/ui/views/treeView.py
SOURCES += ../manuskript/ui/views/cmbOutlineStatusChoser.py
SOURCES += ../manuskript/ui/views/characterTreeView.py
SOURCES += ../manuskript/ui/views/metadataView.py
SOURCES += ../manuskript/ui/views/plotTreeView.py
SOURCES += ../manuskript/ui/views/cmbOutlineCharacterChoser.py
SOURCES += ../manuskript/ui/views/webView.py
SOURCES += ../manuskript/ui/views/textEditView.py
SOURCES += ../manuskript/ui/views/storylineView.py
SOURCES += ../manuskript/ui/views/sldImportance.py
SOURCES += ../manuskript/ui/views/sldImportance_ui.py
SOURCES += ../manuskript/ui/views/basicItemView_ui.py
SOURCES += ../manuskript/ui/views/storylineView_ui.py
SOURCES += ../manuskript/ui/views/MDEditCompleter.py
SOURCES += ../manuskript/ui/views/MDEditView.py
SOURCES += ../manuskript/ui/views/cmbOutlineLabelChoser.py
SOURCES += ../manuskript/ui/views/outlineDelegates.py
SOURCES += ../manuskript/ui/views/outlineBasics.py
SOURCES += ../manuskript/ui/views/propertiesView.py
SOURCES += ../manuskript/ui/views/lineEditView.py
SOURCES += ../manuskript/ui/views/plotDelegate.py
SOURCES += ../manuskript/ui/views/basicItemView.py
SOURCES += ../manuskript/ui/views/treeDelegates.py
SOURCES += ../manuskript/ui/views/chkOutlineCompile.py
SOURCES += ../manuskript/ui/views/dndView.py
SOURCES += ../manuskript/ui/views/corkDelegate.py
SOURCES += ../manuskript/ui/views/PDFViewer.py
SOURCES += ../manuskript/ui/views/propertiesView_ui.py
SOURCES += ../manuskript/ui/collapsibleDockWidgets.py
SOURCES += ../manuskript/ui/collapsibleGroupBox2.py
SOURCES += ../manuskript/ui/welcome_ui.py
SOURCES += ../manuskript/ui/welcome.py
SOURCES += ../manuskript/ui/collapsibleGroupBox.py
SOURCES += ../manuskript/ui/settings_ui.py
SOURCES += ../manuskript/ui/searchMenu.py
SOURCES += ../manuskript/ui/listDialog_ui.py
SOURCES += ../manuskript/ui/about.py
SOURCES += ../manuskript/ui/cheatSheet.py
SOURCES += ../manuskript/ui/statusLabel.py
SOURCES += ../manuskript/ui/search.py
SOURCES += ../manuskript/settingsWindow.py
TRANSLATIONS += manuskript_sv.ts
TRANSLATIONS += manuskript_ta.ts
TRANSLATIONS += manuskript_nb_NO.ts
TRANSLATIONS += manuskript_ca.ts
TRANSLATIONS += manuskript_id.ts
TRANSLATIONS += manuskript_fi.ts
TRANSLATIONS += manuskript_zh_CN.ts
TRANSLATIONS += manuskript_pt.ts
TRANSLATIONS += manuskript_hu.ts
TRANSLATIONS += manuskript_it.ts
TRANSLATIONS += manuskript_sk.ts
TRANSLATIONS += manuskript_pl.ts
TRANSLATIONS += manuskript_tr.ts
TRANSLATIONS += manuskript_es.ts
TRANSLATIONS += manuskript_ru.ts
TRANSLATIONS += manuskript_uk.ts
TRANSLATIONS += manuskript_pt_PT.ts
TRANSLATIONS += manuskript_fr.ts
TRANSLATIONS += manuskript_mr.ts
TRANSLATIONS += manuskript_ja.ts
TRANSLATIONS += manuskript_ar_SA.ts
TRANSLATIONS += manuskript_nl.ts
TRANSLATIONS += manuskript_he.ts
TRANSLATIONS += manuskript_da.ts
TRANSLATIONS += manuskript_de.ts
TRANSLATIONS += manuskript_fa.ts
TRANSLATIONS += manuskript_el.ts
TRANSLATIONS += manuskript_ro.ts
TRANSLATIONS += manuskript_ca@valencia.ts
TRANSLATIONS += manuskript_pt_BR.ts
TRANSLATIONS += manuskript_en_GB.ts
TRANSLATIONS += manuskript_zh_HANT.ts
TRANSLATIONS += manuskript_ko.ts
TRANSLATIONS += manuskript_eo.ts
TRANSLATIONS += manuskript_hr.ts
