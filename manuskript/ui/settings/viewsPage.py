#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib

from manuskript.data import Settings, SettingsKeys
from manuskript.ui.util import rgbaFromHex
from manuskript.ui.settings.abstractPage import AbstractPage
from manuskript.ui.settings.widgetGroup import WidgetGroupBuilder, WidgetGroup


class ViewsPage(AbstractPage):

    def __init__(self, settings: Settings):
        self.settings = settings

        builder = Gtk.Builder()
        builder.add_from_file("ui/settings/views.glade")
        self.treeIconSizeUpdateTimeoutId = None
        
        self.widget = builder.get_object("views_page")

        self.treeIconColor: Gtk.ComboBox = builder.get_object("tree_icon_color")
        self.treeTextColor: Gtk.ComboBox = builder.get_object("tree_text_color")
        self.treeBackgroundColor: Gtk.ComboBox = builder.get_object("tree_background_color")
        self.treeIconSize: Gtk.Scale = builder.get_object("tree_icon_size")
        self.treeCharWordCounter: Gtk.ToggleButton = builder.get_object("tree_char_word_counter")
        self.treeFoldersGroup: WidgetGroup = (WidgetGroupBuilder()
            .addWidget(builder.get_object("tree_folders_item_count"), "Count")
            .addWidget(builder.get_object("tree_folders_word_count"), "WC")
            .addWidget(builder.get_object("tree_folders_char_count"), "CC")
            .addWidget(builder.get_object("tree_folders_progress"), "Progress")
            .addWidget(builder.get_object("tree_folders_summary"), "Summary")
            .addWidget(builder.get_object("tree_folders_nothing"), "Nothing")
            .build()
        )
        self.treeTextGroup: WidgetGroup = (WidgetGroupBuilder()
            .addWidget(builder.get_object("tree_text_word_count"), "WC")
            .addWidget(builder.get_object("tree_text_char_count"), "CC")
            .addWidget(builder.get_object("tree_text_progress"), "Progress")
            .addWidget(builder.get_object("tree_text_summary"), "Summary")
            .addWidget(builder.get_object("tree_text_nothing"), "Nothing")
            .build()
        )
        self.outlineIconColor: Gtk.ComboBox = builder.get_object("outline_icon_color")
        self.outlineTextColor: Gtk.ComboBox = builder.get_object("outline_text_color")
        self.outlineBackgroundColor: Gtk.ComboBox = builder.get_object("outline_background_color")
        self.outlineVisibleColumnsGroup: WidgetGroup = (WidgetGroupBuilder()
            .addWidget(builder.get_object("outline_visible_title"), 0)
            .addWidget(builder.get_object("outline_visible_pov"), 5)
            .addWidget(builder.get_object("outline_visible_label"), 7)
            .addWidget(builder.get_object("outline_visible_status"), 8)
            .addWidget(builder.get_object("outline_visible_compile"), 9)
            .addWidget(builder.get_object("outline_visible_word_count"), 11)
            .addWidget(builder.get_object("outline_visible_goal"), 12)
            .addWidget(builder.get_object("outline_visible_percentage"), 13)
            .build()
        )
        self.indexCardsColorsIconColor: Gtk.ComboBox = builder.get_object("index_cards_colors_icon_color")
        self.indexCardsColorsTextColor: Gtk.ComboBox = builder.get_object("index_cards_colors_text_color")
        self.indexCardsColorsBackgroundColor: Gtk.ComboBox = builder.get_object("index_cards_colors_background_color")
        self.indexCardsColorsBorderColor: Gtk.ComboBox = builder.get_object("index_cards_colors_border_color")
        self.indexCardsColorsCornerColor: Gtk.ComboBox = builder.get_object("index_cards_colors_corner_color")
        self.indexCardsStyleGroup: WidgetGroup = (WidgetGroupBuilder()
            .addWidget(builder.get_object("index_card_old_style"), "old")
            .addWidget(builder.get_object("index_card_new_style"), "new")
            .build()
        )
        self.indexCardsBackgroundColor: Gtk.ColorButton = builder.get_object("index_cards_background_color")
        self.indexCardsBackgroundImage: Gtk.FileChooser = builder.get_object("index_cards_background_image")
        self.textEditorColorsBackground: Gtk.ColorButton = builder.get_object("text_editor_colors_background")
        self.textEditorColorsForeground: Gtk.ColorButton = builder.get_object("text_editor_colors_foreground")
        self.textEditorColorsRestoreDefaults: Gtk.Button = builder.get_object("text_editor_colors_restore_defaults")
        self.textEditorFontFamily: Gtk.FontButton = builder.get_object("text_editor_font_family")
        self.textEditorFontSize: Gtk.SpinButton = builder.get_object("text_editor_font_size")
        self.textEditorMisspelled: Gtk.ColorButton = builder.get_object("text_editor_misspelled")
        self.textEditorTextAreaMaxWidth: Gtk.CheckButton = builder.get_object("text_editor_text_area_max_width")
        self.textEditorTextAreaWidth: Gtk.SpinButton = builder.get_object("text_editor_text_area_width")
        self.textEditorTextAreaTopBottomMargins: Gtk.SpinButton = builder.get_object("text_editor_text_area_top_bottom_margins")
        self.textEditorTextAreaLeftRightMargins: Gtk.SpinButton = builder.get_object("text_editor_text_area_left_right_margins")
        self.textEditorParagraphsAlignment: Gtk.ComboBox = builder.get_object("text_editor_paragraphs_alignment")
        self.textEditorParagraphsLineSpacing: Gtk.ComboBox = builder.get_object("text_editor_paragraphs_line_spacing")
        self.textEditorParagraphsLineSpacingProportional: Gtk.SpinButton = builder.get_object("text_editor_paragraphs_line_spacing_proportional")
        self.textEditorParagraphsTabWidth: Gtk.SpinButton = builder.get_object("text_editor_paragraphs_tab_width")
        self.textEditorParagraphsIndentFirstLine: Gtk.ToggleButton = builder.get_object("text_editor_paragraphs_indent_first_line")
        self.textEditorParagraphsSpacingAbove: Gtk.SpinButton = builder.get_object("text_editor_paragraphs_spacing_above")
        self.textEditorParagraphsSpacingBelow: Gtk.SpinButton = builder.get_object("text_editor_paragraphs_spacing_below")
        self.textEditorCursorBlockInsertion: Gtk.ToggleButton = builder.get_object("text_editor_cursor_block_insertion")
        self.textEditorCursorBlockInsertionSize: Gtk.SpinButton = builder.get_object("text_editor_cursor_block_insertion_size")
        self.textEditorCursorDisableBlinking: Gtk.ToggleButton = builder.get_object("text_editor_cursor_disable_blinking")
        self.textEditorCursorTypewriterMode: Gtk.ToggleButton = builder.get_object("text_editor_cursor_typewriter_mode")
        self.textEditorCursorFocusMode: Gtk.ComboBox = builder.get_object("text_editor_cursor_focus_mode")

        self.setActiveComboItem(self.treeIconColor, settings.get(SettingsKeys.ViewSettings.Tree.ICON), 0)
        self.setActiveComboItem(self.treeTextColor, settings.get(SettingsKeys.ViewSettings.Tree.TEXT), 0)
        self.setActiveComboItem(self.treeTextColor, settings.get(SettingsKeys.ViewSettings.Tree.BACKGROUND), 0)
        self.treeIconSize.set_value(settings.get(SettingsKeys.ViewSettings.Tree.ICON_SIZE))
        self.treeCharWordCounter.set_active(settings.get(SettingsKeys.COUNT_SPACES))
        self.treeFoldersGroup.setActiveFromSelection(settings.get(SettingsKeys.ViewSettings.Tree.INFO_FOLDER))
        self.treeTextGroup.setActiveFromSelection(settings.get(SettingsKeys.ViewSettings.Tree.INFO_TEXT))
        self.setActiveComboItem(self.outlineIconColor, settings.get(SettingsKeys.ViewSettings.Outline.ICON), 0)
        self.setActiveComboItem(self.outlineTextColor, settings.get(SettingsKeys.ViewSettings.Outline.TEXT), 0)
        self.setActiveComboItem(self.outlineBackgroundColor, settings.get(SettingsKeys.ViewSettings.Outline.BACKGROUND), 0)        
        self.outlineVisibleColumnsGroup.setActiveFromSelection(settings.get(SettingsKeys.OUTLINE_VIEW_COLUMNS))
        self.setActiveComboItem(self.indexCardsColorsIconColor, settings.get(SettingsKeys.ViewSettings.Cork.ICON), 0)
        self.setActiveComboItem(self.indexCardsColorsTextColor, settings.get(SettingsKeys.ViewSettings.Cork.TEXT), 0)
        self.setActiveComboItem(self.indexCardsColorsBackgroundColor, settings.get(SettingsKeys.ViewSettings.Cork.BACKGROUND), 0)
        self.setActiveComboItem(self.indexCardsColorsBorderColor, settings.get(SettingsKeys.ViewSettings.Cork.BORDER), 0)
        self.setActiveComboItem(self.indexCardsColorsCornerColor, settings.get(SettingsKeys.ViewSettings.Cork.CORNER), 0)
        self.indexCardsStyleGroup.setActiveFromSelection(settings.get(SettingsKeys.CORK_STYLE))        
        self.indexCardsBackgroundColor.set_rgba(rgbaFromHex(settings.get(SettingsKeys.CorkBackground.COLOR)))
        self.indexCardsBackgroundImage.set_filename(settings.get(SettingsKeys.CorkBackground.IMAGE))
        self.textEditorColorsBackground.set_rgba(rgbaFromHex(settings.get(SettingsKeys.TextEditor.BACKGROUND)))
        self.textEditorColorsForeground.set_rgba(rgbaFromHex(settings.get(SettingsKeys.TextEditor.FONT_COLOR)))
        self.textEditorFontFamily.set_font(self.extractFontName(settings.get(SettingsKeys.TextEditor.FONT)))
        self.textEditorFontSize.set_value(self.extractFontSize(settings.get(SettingsKeys.TextEditor.FONT)))
        self.textEditorMisspelled.set_rgba(rgbaFromHex(settings.get(SettingsKeys.TextEditor.MISSPELLED)))
        maxWidth=settings.get(SettingsKeys.TextEditor.MAX_WIDTH)
        self.textEditorTextAreaMaxWidth.set_active(maxWidth==0)
        self.textEditorTextAreaWidth.set_sensitive(maxWidth>0)
        self.textEditorTextAreaWidth.set_value(maxWidth)
        self.textEditorTextAreaTopBottomMargins.set_value(settings.get(SettingsKeys.TextEditor.MARGINS_TB))
        self.textEditorTextAreaLeftRightMargins.set_value(settings.get(SettingsKeys.TextEditor.MARGINS_LR))
        self.setActiveComboItem(self.textEditorParagraphsAlignment, settings.get(SettingsKeys.TextEditor.TEXT_ALIGNMENT), 3)        
        
        # Proportional spacing represents all possible values, but 100, 150 and 200.
        spacingSetting=settings.get(SettingsKeys.TextEditor.LINE_SPACING)
        if spacingSetting in [100, 150, 200]:
            self.setActiveComboItem(self.textEditorParagraphsLineSpacing, spacingSetting, 1)
            self.textEditorParagraphsLineSpacingProportional.set_sensitive(False)
        else:
            self.setActiveComboItem(self.textEditorParagraphsLineSpacing, 0, 1)
            self.textEditorParagraphsLineSpacingProportional.set_sensitive(True)

        self.textEditorParagraphsLineSpacingProportional.set_value(settings.get(SettingsKeys.TextEditor.LINE_SPACING))
        self.textEditorParagraphsTabWidth.set_value(settings.get(SettingsKeys.TextEditor.TAB_WIDTH))
        self.textEditorParagraphsIndentFirstLine.set_active(settings.get(SettingsKeys.TextEditor.INDENT))
        self.textEditorParagraphsSpacingAbove.set_value(settings.get(SettingsKeys.TextEditor.SPACING_ABOVE))
        self.textEditorParagraphsSpacingBelow.set_value(settings.get(SettingsKeys.TextEditor.SPACING_BELOW))

        cursorBlockSize = settings.get(SettingsKeys.TextEditor.CURSOR_WIDTH)
        if cursorBlockSize == 1:
            self.textEditorCursorBlockInsertion.set_active(False)
            self.textEditorCursorBlockInsertionSize.set_sensitive(False)
            self.textEditorCursorBlockInsertionSize.set_value(9)
        else:
            self.textEditorCursorBlockInsertion.set_active(True)
            self.textEditorCursorBlockInsertionSize.set_sensitive(True)
            self.textEditorCursorBlockInsertionSize.set_value(cursorBlockSize)
        self.textEditorCursorDisableBlinking.set_active(settings.get(SettingsKeys.TextEditor.CURSOR_NOT_BLINKING))

        # Original manuskript discrepency, "always center" is used as "typewriter mode"
        self.textEditorCursorTypewriterMode.set_active(settings.get(SettingsKeys.TextEditor.ALWAYS_CENTER)) 
        focusMode=settings.get(SettingsKeys.TextEditor.FOCUS_MODE)
        if not focusMode:
            focusMode="none"
        
        self.setActiveComboItem(self.textEditorCursorFocusMode, focusMode, 1)

        self.treeIconColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Tree.ICON})
        self.treeTextColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Tree.TEXT})
        self.treeBackgroundColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Tree.BACKGROUND})
        self.treeIconSize.connect("value-changed", self._treeIconSizeChanged)
        self.treeCharWordCounter.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.COUNT_SPACES)
        self.treeFoldersGroup.connect("toggled", self._genericToggleButtonGroupToggled, SettingsKeys.ViewSettings.Tree.INFO_FOLDER)
        self.treeTextGroup.connect("toggled", self._genericToggleButtonGroupToggled, SettingsKeys.ViewSettings.Tree.INFO_TEXT)
        self.outlineIconColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Outline.ICON})
        self.outlineTextColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Outline.TEXT})
        self.outlineBackgroundColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Outline.BACKGROUND})
        self.outlineVisibleColumnsGroup.connect("toggled", self._oulineVisibleColumnsToggled)
        self.indexCardsColorsIconColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Cork.ICON})
        self.indexCardsColorsTextColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Cork.TEXT})
        self.indexCardsColorsBackgroundColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Cork.BACKGROUND})
        self.indexCardsColorsBorderColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Cork.BORDER})
        self.indexCardsColorsCornerColor.connect("changed", self._genericComboChanged, {'column': 0, 'settingsKey': SettingsKeys.ViewSettings.Cork.CORNER})
        self.indexCardsStyleGroup.connect("toggled", self._indexCardsColorsStyleChanged)
        self.indexCardsBackgroundColor.connect("color-set", self._genericColorButtonColorSet, SettingsKeys.CorkBackground.COLOR)
        self.indexCardsBackgroundImage.connect("file-set", self._indexCardsBackgroundImageFileSet)
        self.textEditorColorsBackground.connect("color-set", self._genericColorButtonColorSet, SettingsKeys.TextEditor.BACKGROUND)
        self.textEditorColorsForeground.connect("color-set", self._genericColorButtonColorSet, SettingsKeys.TextEditor.FONT_COLOR)
        self.textEditorColorsRestoreDefaults.connect("clicked", self._textEditorColorsRestoreDefaultsClicked)
        self.textEditorFontFamily.connect("font-set", self._textEditorFontFamilyFontSet)
        self.textEditorFontSize.connect("value-changed", self._textEditorFontSizeValueChanged)
        self.textEditorMisspelled.connect("color-set", self._genericColorButtonColorSet, SettingsKeys.TextEditor.MISSPELLED)
        self.textEditorTextAreaMaxWidth.connect("toggled", self._textEditorTextAreaMaxWidthToggled)
        self.textEditorTextAreaWidth.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.MAX_WIDTH)
        self.textEditorTextAreaTopBottomMargins.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.MARGINS_TB)
        self.textEditorTextAreaLeftRightMargins.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.MARGINS_LR)
        self.textEditorParagraphsAlignment.connect("changed", self._genericComboChanged, {'column': 3, 'settingsKey': SettingsKeys.TextEditor.TEXT_ALIGNMENT})
        self.textEditorParagraphsLineSpacing.connect("changed", self._textEditorParagraphsLineSpacingChanged)
        self.textEditorParagraphsLineSpacingProportional.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.LINE_SPACING)
        self.textEditorParagraphsTabWidth.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.TAB_WIDTH)
        self.textEditorParagraphsIndentFirstLine.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.TextEditor.INDENT)
        self.textEditorParagraphsSpacingAbove.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.SPACING_ABOVE)
        self.textEditorParagraphsSpacingBelow.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.SPACING_BELOW)
        self.textEditorCursorBlockInsertion.connect("toggled", self._textEditorCursorBlockInsertionToggled, SettingsKeys.TextEditor.CURSOR_WIDTH)
        self.textEditorCursorBlockInsertionSize.connect("value-changed", self._genericSpinButtonValueChanged, SettingsKeys.TextEditor.CURSOR_WIDTH)
        self.textEditorCursorDisableBlinking.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.TextEditor.CURSOR_NOT_BLINKING)
        self.textEditorCursorTypewriterMode.connect("toggled", self._genericToggleButtonToggled, SettingsKeys.TextEditor.ALWAYS_CENTER)
        self.textEditorCursorFocusMode.connect("changed", self._textEditorCurosFocusModeChanged)

    def _treeIconSizeChanged(self, scale: Gtk.Scale):
        if self.treeIconSizeUpdateTimeoutId is not None:
            GLib.source_remove(self.treeIconSizeUpdateTimeoutId)
            self.treeIconSizeUpdateTimeoutId = None

        self.treeIconSizeUpdateTimeoutId = GLib.timeout_add(300, self._applyTreeIconSize, scale.get_value())

    def _applyTreeIconSize(self, value: float):
        self.settings.set(SettingsKeys.ViewSettings.Tree.ICON_SIZE, int(value))

        self.treeIconSizeUpdateTimeoutId = None
        return False 

    def _outlineBackgroundColorChanged(self, combo: Gtk.ComboBox):
        value = self.getComboSelectedValue(combo, 0)

        self.settings.set(SettingsKeys.ViewSettings.Outline.BACKGROUND, value)

    def _oulineVisibleColumnsToggled(self, checkbutton: Gtk.CheckButton, *args):
        self.settings.set(SettingsKeys.OUTLINE_VIEW_COLUMNS, self.outlineVisibleColumnsGroup.fetchAllActive())

    def _indexCardsColorsStyleChanged(self, button: Gtk.RadioButton, value):
        if button.get_active():
            self.settings.set(SettingsKeys.CORK_STYLE, value)

    def _indexCardsBackgroundImageFileSet(self, button: Gtk.FileChooser):
        self.settings.set(SettingsKeys.CorkBackground.IMAGE, button.get_filename())

    def _textEditorColorsRestoreDefaultsClicked(self, button: Gtk.Button):
        backgroundColor="#ffffff"
        foregroundColor="#1a1a1a"
        self.settings.set(SettingsKeys.TextEditor.BACKGROUND, backgroundColor)
        self.settings.set(SettingsKeys.TextEditor.FONT_COLOR, foregroundColor)
        self.textEditorColorsBackground.set_rgba(rgbaFromHex(backgroundColor))
        self.textEditorColorsForeground.set_rgba(rgbaFromHex(foregroundColor))

    def extractFontName(self, fontString: str) -> str:
        parts = fontString.split(',')
        return parts[0]

    def extractFontSize(self, fontString: str) -> int:
        parts = fontString.split(',')
        return int(parts[1])

    def replaceFontName(self, fontString: str, newFontName: str) -> str:
        parts = fontString.split(',')
        parts[0] = newFontName
        return ','.join(parts)

    def replaceFontSize(self, fontString: str, newFontSize: int) -> str:
        parts = fontString.split(',')
        parts[1] = str(newFontSize)
        return ','.join(parts)
    
    def _textEditorFontFamilyFontSet(self, button: Gtk.FontButton):
        currentFont=self.settings.get(SettingsKeys.TextEditor.FONT)
        pangoFont=button.get_font_face()
        self.settings.set(SettingsKeys.TextEditor.FONT, self.replaceFontName(currentFont, str(pangoFont.get_family().get_name())))

    def _textEditorFontSizeValueChanged(self, button: Gtk.SpinButton):
        currentFont=self.settings.get(SettingsKeys.TextEditor.FONT)
        self.settings.set(SettingsKeys.TextEditor.FONT, self.replaceFontSize(currentFont, button.get_value_as_int()))

    def _textEditorTextAreaMaxWidthToggled(self, button: Gtk.ToggleButton):
        if button.get_active():
            self.settings.set(SettingsKeys.TextEditor.MAX_WIDTH, 0)
            self.textEditorTextAreaWidth.set_sensitive(False)
        else:
            lastEditedValue=self.textEditorTextAreaWidth.get_value_as_int()

            if lastEditedValue==0.0:
                lastEditedValue=600.0

            self.settings.set(SettingsKeys.TextEditor.MAX_WIDTH, lastEditedValue)
            self.textEditorTextAreaWidth.set_value(lastEditedValue)
            self.textEditorTextAreaWidth.set_sensitive(True)

    def _textEditorParagraphsLineSpacingChanged(self, combo: Gtk.ComboBox):
        value = self.getComboSelectedValue(combo, 1)

        if value!=0:
            self.settings.set(SettingsKeys.TextEditor.LINE_SPACING, value)
            self.textEditorParagraphsLineSpacingProportional.set_sensitive(False)
        else:
            self.settings.set(SettingsKeys.TextEditor.LINE_SPACING, self.textEditorParagraphsLineSpacingProportional.get_value_as_int())
            self.textEditorParagraphsLineSpacingProportional.set_sensitive(True)

    def _textEditorCursorBlockInsertionToggled(self, button: Gtk.ToggleButton, settingsKey: str):
        if button.get_active():
            self.settings.set(settingsKey, self.textEditorCursorBlockInsertionSize.get_value_as_int())
            self.textEditorCursorBlockInsertionSize.set_sensitive(True)
        else:
            self.settings.set(settingsKey, 1)
            self.textEditorCursorBlockInsertionSize.set_sensitive(False)

    def _textEditorCurosFocusModeChanged(self, combo: Gtk.ComboBox):
        value = self.getComboSelectedValue(combo, 1)
        if value == "none":
            value=False
        self.settings.set(SettingsKeys.TextEditor.FOCUS_MODE, value)