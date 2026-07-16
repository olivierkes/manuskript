#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for sidebar labels feature."""

import json
import pytest


class TestSidebarLabelsSetting:
    """Test suite for the showSidebarLabels setting."""

    def test_setting_exists(self):
        """Test that the show_sidebar_labels setting exists in settings module."""
        from manuskript import settings

        assert hasattr(settings, 'show_sidebar_labels'), \
            "show_sidebar_labels setting missing from settings module"

    def test_default_value_is_false(self):
        """Test that show_sidebar_labels defaults to False (labels hidden)."""
        from manuskript import settings

        assert settings.show_sidebar_labels is False, \
            f"Expected False, got {settings.show_sidebar_labels}"

    def test_save_setting(self):
        """Test that show_sidebar_labels is correctly saved."""
        from manuskript import settings

        # Set to True and save
        settings.show_sidebar_labels = True
        saved_data = settings.save()
        parsed = json.loads(saved_data)

        assert 'show_sidebar_labels' in parsed, \
            "show_sidebar_labels not found in saved data"
        assert parsed['show_sidebar_labels'] is True, \
            f"Expected True in saved data, got {parsed['show_sidebar_labels']}"

        # Cleanup
        settings.show_sidebar_labels = False

    def test_load_setting(self):
        """Test that show_sidebar_labels is correctly loaded."""
        from manuskript import settings

        # Create save data with setting enabled
        settings.show_sidebar_labels = True
        saved_data = settings.save()

        # Reset and load
        settings.show_sidebar_labels = False
        settings.load(saved_data)

        assert settings.show_sidebar_labels is True, \
            f"Expected True after load, got {settings.show_sidebar_labels}"

        # Cleanup
        settings.show_sidebar_labels = False

    @pytest.mark.parametrize("value", [True, False])
    def test_save_load_roundtrip(self, value):
        """Test save/load roundtrip with both True and False values."""
        from manuskript import settings

        # Set value, save, reset, load
        settings.show_sidebar_labels = value
        saved_data = settings.save()
        settings.show_sidebar_labels = not value
        settings.load(saved_data)

        assert settings.show_sidebar_labels is value, \
            f"Roundtrip failed: expected {value}, got {settings.show_sidebar_labels}"

        # Cleanup
        settings.show_sidebar_labels = False


class TestSidebarLabelsUI:
    """Test suite for sidebar labels UI components."""

    def test_checkbox_exists_in_settings_ui(self, MWSampleProject):
        """Test that chkshow_sidebar_labels checkbox exists in settings UI."""
        from manuskript.ui.settings_ui import Ui_Settings

        # Use existing settings window from mainWindow
        mw = MWSampleProject
        mw.actSettings.triggered.emit()
        sw = mw.sw

        assert hasattr(sw, 'chkshow_sidebar_labels'), \
            "chkshow_sidebar_labels checkbox missing from settings UI"

        sw.close()

    def test_mainwindow_has_method(self):
        """Test that MainWindow has set_sidebar_labels_visible method."""
        from manuskript.mainWindow import MainWindow

        assert hasattr(MainWindow, 'set_sidebar_labels_visible'), \
            "set_sidebar_labels_visible method missing from MainWindow"
        assert callable(getattr(MainWindow, 'set_sidebar_labels_visible')), \
            "set_sidebar_labels_visible is not callable"

    def test_settings_window_has_handler(self):
        """Test that settingsWindow has sidebarSettingsChanged handler."""
        from manuskript.settingsWindow import settingsWindow

        assert hasattr(settingsWindow, 'sidebarSettingsChanged'), \
            "sidebarSettingsChanged method missing from settingsWindow"
        assert callable(getattr(settingsWindow, 'sidebarSettingsChanged')), \
            "sidebarSettingsChanged is not callable"


class TestSidebarLabelsIntegration:
    """Integration tests for sidebar labels feature."""

    def test_settings_window_checkbox_integration(self, MWSampleProject):
        """Test checkbox integration with settings in settingsWindow."""
        mw = MWSampleProject
        from manuskript import settings

        # Open settings window
        mw.actSettings.triggered.emit()
        assert mw.sw.isVisible()

        sw = mw.sw

        # Test initial state matches settings
        initial_state = settings.show_sidebar_labels
        assert sw.chkshow_sidebar_labels.isChecked() == initial_state, \
            "Checkbox state doesn't match settings on open"

        # Toggle checkbox
        sw.chkshow_sidebar_labels.setChecked(not initial_state)
        assert settings.show_sidebar_labels == (not initial_state), \
            "Settings not updated when checkbox toggled"

        # Restore original state
        settings.show_sidebar_labels = initial_state
        sw.close()

    def test_mainwindow_sidebar_visibility(self, MWSampleProject):
        """Test that set_sidebar_labels_visible changes lstTabs appearance."""
        mw = MWSampleProject

        # Hide labels (should be 48px)
        mw.set_sidebar_labels_visible(False)
        hidden_width = mw.lstTabs.width()
        assert hidden_width == 48, \
            f"Expected width 48 for hidden labels, got {hidden_width}"

        # Show labels (should be 120px)
        mw.set_sidebar_labels_visible(True)
        shown_width = mw.lstTabs.width()
        assert shown_width == 120, \
            f"Expected width 120 for shown labels, got {shown_width}"

        # Verify items have text when shown
        for i in range(mw.lstTabs.count()):
            item = mw.lstTabs.item(i)
            if not item.isHidden():
                assert item.text() != "", \
                    f"Item {i} should have text when labels shown"

        # Hide again and verify no text
        mw.set_sidebar_labels_visible(False)
        for i in range(mw.lstTabs.count()):
            item = mw.lstTabs.item(i)
            if not item.isHidden():
                assert item.text() == "", \
                    f"Item {i} should have no text when labels hidden"

    def test_dock_navigation_follows_lsttabs_width(self, MWSampleProject):
        """Test that dckNavigation width follows lstTabs width constraints."""
        mw = MWSampleProject

        # Hide labels - both should be 48px
        mw.set_sidebar_labels_visible(False)
        assert mw.lstTabs.minimumWidth() == 48, \
            "lstTabs minimum width should be 48 when hidden"
        assert mw.lstTabs.maximumWidth() == 48, \
            "lstTabs maximum width should be 48 when hidden"
        assert mw.dckNavigation.minimumWidth() == 48, \
            "dckNavigation minimum width should be 48 when hidden"
        assert mw.dckNavigation.maximumWidth() == 48, \
            "dckNavigation maximum width should be 48 when hidden"

        # Show labels - both should be 120px
        mw.set_sidebar_labels_visible(True)
        assert mw.lstTabs.minimumWidth() == 120, \
            "lstTabs minimum width should be 120 when shown"
        assert mw.lstTabs.maximumWidth() == 120, \
            "lstTabs maximum width should be 120 when shown"
        assert mw.dckNavigation.minimumWidth() == 120, \
            "dckNavigation minimum width should be 120 when shown"
        assert mw.dckNavigation.maximumWidth() == 120, \
            "dckNavigation maximum width should be 120 when shown"

    def test_item_size_hints_change_with_visibility(self, MWSampleProject):
        """Test that list item size hints change appropriately."""
        mw = MWSampleProject

        # Hide labels - items should be 48x48
        mw.set_sidebar_labels_visible(False)
        for i in range(mw.lstTabs.count()):
            item = mw.lstTabs.item(i)
            if not item.isHidden():
                size_hint = item.sizeHint()
                assert size_hint.width() == 48, \
                    f"Item {i} width should be 48 when hidden, got {size_hint.width()}"
                assert size_hint.height() == 48, \
                    f"Item {i} height should be 48 when hidden, got {size_hint.height()}"

        # Show labels - items should be 120x64
        mw.set_sidebar_labels_visible(True)
        for i in range(mw.lstTabs.count()):
            item = mw.lstTabs.item(i)
            if not item.isHidden():
                size_hint = item.sizeHint()
                assert size_hint.width() == 120, \
                    f"Item {i} width should be 120 when shown, got {size_hint.width()}"
                assert size_hint.height() == 64, \
                    f"Item {i} height should be 64 when shown, got {size_hint.height()}"

    def test_spacing_set_to_zero(self, MWSampleProject):
        """Test that lstTabs spacing is set to 0 to prevent gaps."""
        mw = MWSampleProject

        # Test with labels hidden
        mw.set_sidebar_labels_visible(False)
        assert mw.lstTabs.spacing() == 0, \
            "lstTabs spacing should be 0 when labels hidden"

        # Test with labels shown
        mw.set_sidebar_labels_visible(True)
        assert mw.lstTabs.spacing() == 0, \
            "lstTabs spacing should be 0 when labels shown"

    def test_toggle_multiple_times(self, MWSampleProject):
        """Test toggling visibility multiple times maintains correct state."""
        mw = MWSampleProject

        for cycle in range(3):
            # Show labels
            mw.set_sidebar_labels_visible(True)
            assert mw.lstTabs.width() == 120, \
                f"Cycle {cycle}: Width should be 120 when shown"
            assert mw.dckNavigation.width() == 120, \
                f"Cycle {cycle}: Dock width should be 120 when shown"

            # Hide labels
            mw.set_sidebar_labels_visible(False)
            assert mw.lstTabs.width() == 48, \
                f"Cycle {cycle}: Width should be 48 when hidden"
            assert mw.dckNavigation.width() == 48, \
                f"Cycle {cycle}: Dock width should be 48 when hidden"


if __name__ == '__main__':
    # Allow running with: python test_sidebar_labels.py
    pytest.main([__file__, '-v'])
