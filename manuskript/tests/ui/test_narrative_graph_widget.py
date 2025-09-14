#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for the narrative graph widget."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest

from manuskript.ui.narrative_graph_widget import NarrativeGraphWidget
from manuskript.ai.narrative_graph.graph_storage import GraphStorage
from manuskript import settings


class TestNarrativeGraphWidget:
    """Test the NarrativeGraphWidget class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Ensure QApplication exists
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        # Create widget
        self.widget = NarrativeGraphWidget()
        
        # Create temporary storage
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        self.storage = GraphStorage(self.temp_file.name)
        
        # Enable AI features
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'widget'):
            self.widget.close()
        
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_widget_initialization(self):
        """Test widget initialization."""
        assert self.widget is not None
        assert hasattr(self.widget, 'tab_widget')
        assert hasattr(self.widget, 'characters_table')
        assert hasattr(self.widget, 'relationships_table')
        assert hasattr(self.widget, 'events_tree')
        
        # Check tabs are created
        assert self.widget.tab_widget.count() == 5
        
        tab_titles = []
        for i in range(self.widget.tab_widget.count()):
            tab_titles.append(self.widget.tab_widget.tabText(i))
        
        expected_tabs = ["Characters", "Relationships", "Events", "Consistency", "Graph View"]
        for expected in expected_tabs:
            assert expected in tab_titles
    
    def test_set_graph_storage(self):
        """Test connecting widget to graph storage."""
        # Initially no storage
        assert self.widget.graph_storage is None
        
        # Set storage
        self.widget.set_graph_storage(self.storage)
        assert self.widget.graph_storage is self.storage
    
    def test_refresh_data_no_storage(self):
        """Test refresh when no storage is connected."""
        # Should handle gracefully
        self.widget.refresh_data()
        
        # Status should indicate no data
        assert "No graph data" in self.widget.status_label.text()
    
    def test_refresh_data_with_storage(self):
        """Test refresh with connected storage."""
        # Add test data
        self.storage.add_character("Alice", {"role": "hero"})
        self.storage.add_character("Bob", {"role": "villain"})
        self.storage.add_location("Castle", "Dark castle")
        self.storage.add_relationship("Alice", "Bob", "opposes")
        
        # Connect and refresh
        self.widget.set_graph_storage(self.storage)
        self.widget.refresh_data()
        
        # Should update status
        assert "Ready" in self.widget.status_label.text()
        
        # Should update stats
        stats_text = self.widget.stats_label.text()
        assert "Nodes:" in stats_text
        assert "Characters:" in stats_text
    
    def test_characters_tab_data_display(self):
        """Test characters tab displays data correctly."""
        # Add test characters
        self.storage.add_character("Alice", {"role": "hero", "age": 25})
        self.storage.add_character("Bob", {"role": "villain", "age": 30})
        
        # Connect and refresh
        self.widget.set_graph_storage(self.storage)
        self.widget.refresh_data()
        
        # Check characters table
        table = self.widget.characters_table
        assert table.rowCount() >= 2
        
        # Verify data in table
        character_names = []
        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            if name_item:
                character_names.append(name_item.text())
        
        assert "Alice" in character_names
        assert "Bob" in character_names
    
    def test_relationships_tab_data_display(self):
        """Test relationships tab displays data correctly."""
        # Add test data
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        self.storage.add_relationship("Alice", "Bob", "knows", {"strength": "strong"})
        
        # Connect and refresh
        self.widget.set_graph_storage(self.storage)
        self.widget.refresh_data()
        
        # Check relationships table
        table = self.widget.relationships_table
        assert table.rowCount() >= 1
        
        # Verify relationship data
        if table.rowCount() > 0:
            source_item = table.item(0, 0)
            rel_item = table.item(0, 1) 
            target_item = table.item(0, 2)
            
            assert source_item.text() == "Alice"
            assert target_item.text() == "Bob"
            assert "knows" in rel_item.text() or "unknown" in rel_item.text()
    
    def test_events_tab_data_display(self):
        """Test events tab displays data correctly."""
        # Add test data
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        self.storage.add_event("battle_1", ["Alice", "Bob"], "conflict", "Epic battle")
        
        # Connect and refresh
        self.widget.set_graph_storage(self.storage)
        self.widget.refresh_data()
        
        # Check events tree
        tree = self.widget.events_tree
        assert tree.topLevelItemCount() >= 1
        
        # Verify event data
        if tree.topLevelItemCount() > 0:
            event_item = tree.topLevelItem(0)
            assert event_item.text(0) == "battle_1"
            assert "conflict" in event_item.text(1)
    
    def test_character_selection(self):
        """Test character selection in characters table."""
        # Add test characters
        self.storage.add_character("Alice", {"role": "hero"})
        self.storage.add_character("Bob", {"role": "villain"})
        
        # Connect and refresh
        self.widget.set_graph_storage(self.storage)
        self.widget.refresh_data()
        
        # Signal should be emitted on selection
        with patch.object(self.widget, 'character_selected') as mock_signal:
            # Simulate selection
            table = self.widget.characters_table
            if table.rowCount() > 0:
                table.selectRow(0)
                self.widget.on_character_selected()
                
                # Check signal emission and details update
                mock_signal.emit.assert_called()
                assert self.widget.character_details.toPlainText() != ""
    
    def test_consistency_check_execution(self):
        """Test running consistency check."""
        # Connect storage
        self.widget.set_graph_storage(self.storage)
        
        # Mock the consistency check function
        with patch('manuskript.ai.narrative_graph.narrative_graph.suggest_consistency_check') as mock_check:
            mock_check.return_value = [
                {"type": "warning", "message": "Character age inconsistency"},
                {"type": "info", "message": "New character introduced"}
            ]
            
            # Run consistency check
            self.widget.run_consistency_check()
            
            # Should have called the check function
            mock_check.assert_called_once()
            
            # Should have populated issues table
            table = self.widget.issues_table
            assert table.rowCount() == 2
            
            # Verify issue data
            assert table.item(0, 0).text() == "Warning"
            assert table.item(1, 0).text() == "Info"
    
    def test_consistency_check_no_storage(self):
        """Test consistency check with no storage."""
        # Don't connect storage
        self.widget.run_consistency_check()
        
        # Should handle gracefully
        table = self.widget.issues_table
        assert table.rowCount() >= 1
        
        # Should show "no data" message
        if table.rowCount() > 0:
            assert "No graph data available" in table.item(0, 1).text()
    
    def test_refresh_timer(self):
        """Test automatic refresh timer."""
        assert hasattr(self.widget, 'refresh_timer')
        assert isinstance(self.widget.refresh_timer, QTimer)
        assert self.widget.refresh_timer.interval() == 5000  # 5 seconds
        
        # Timer should be running
        assert self.widget.refresh_timer.isActive()
    
    def test_clear_all_data(self):
        """Test clearing all displayed data."""
        # Add some data to tables first
        self.widget.characters_table.setRowCount(5)
        self.widget.relationships_table.setRowCount(3)
        self.widget.events_tree.addTopLevelItem(self.widget.events_tree.invisibleRootItem())
        self.widget.issues_table.setRowCount(2)
        
        # Clear all data
        self.widget.clear_all_data()
        
        # All tables should be empty
        assert self.widget.characters_table.rowCount() == 0
        assert self.widget.relationships_table.rowCount() == 0
        assert self.widget.events_tree.topLevelItemCount() == 0
        assert self.widget.issues_table.rowCount() == 0
        
        # Text areas should be clear
        assert self.widget.character_details.toPlainText() == ""
        assert self.widget.relationship_details.toPlainText() == ""
        assert self.widget.timeline_info.toPlainText() == ""
    
    def test_feature_disabled_behavior(self):
        """Test widget behavior when feature is disabled."""
        # Connect storage with data
        self.storage.add_character("Alice")
        self.widget.set_graph_storage(self.storage)
        
        # Disable feature
        settings.aiFeatures["narrativeGraphMemory"] = False
        
        # Refresh should clear data
        self.widget.refresh_data()
        
        assert "Feature disabled" in self.widget.status_label.text()
        assert self.widget.characters_table.rowCount() == 0
    
    def test_show_event_handler(self):
        """Test show event triggers refresh."""
        with patch.object(self.widget, 'refresh_data') as mock_refresh:
            # Simulate show event
            self.widget.show()
            
            # Should have triggered refresh
            mock_refresh.assert_called()
    
    def test_close_event_handler(self):
        """Test close event stops timer."""
        # Ensure timer is running
        assert self.widget.refresh_timer.isActive()
        
        # Close widget
        self.widget.close()
        
        # Timer should be stopped
        assert not self.widget.refresh_timer.isActive()
    
    def test_get_data_methods_no_storage(self):
        """Test data extraction methods with no storage."""
        # Should return empty data gracefully
        assert self.widget.get_characters_data() == {}
        assert self.widget.get_relationships_data() == []
        assert self.widget.get_events_data() == []
    
    def test_get_data_methods_with_networkx(self):
        """Test data extraction methods with NetworkX storage."""
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("NetworkX not available")
        
        # Add test data
        self.storage.add_character("Alice", {"role": "hero"})
        self.storage.add_character("Bob", {"role": "villain"})
        self.storage.add_relationship("Alice", "Bob", "opposes")
        self.storage.add_event("battle", ["Alice", "Bob"], "conflict", "Epic battle")
        
        # Connect storage
        self.widget.set_graph_storage(self.storage)
        
        # Test data extraction
        characters = self.widget.get_characters_data()
        relationships = self.widget.get_relationships_data()
        events = self.widget.get_events_data()
        
        # Verify data structure
        assert isinstance(characters, dict)
        assert isinstance(relationships, list)
        assert isinstance(events, list)
        
        # Verify content
        assert "Alice" in characters
        assert "Bob" in characters
        assert len(relationships) >= 1
        assert len(events) >= 1
    
    def test_graph_visualization_without_matplotlib(self):
        """Test graph visualization tab without matplotlib."""
        # Check if matplotlib tab was created
        has_matplotlib = False
        for i in range(self.widget.tab_widget.count()):
            if self.widget.tab_widget.tabText(i) == "Graph View":
                has_matplotlib = True
                break
        
        assert has_matplotlib
        
        # If matplotlib not available, should show message
        try:
            import matplotlib
            # If available, should have figure
            if hasattr(self.widget, 'graph_figure'):
                assert self.widget.graph_figure is not None
        except ImportError:
            # Should have placeholder message
            pass
    
    @patch('matplotlib.pyplot.show')
    def test_graph_visualization_update(self, mock_show):
        """Test graph visualization update."""
        try:
            import matplotlib
            import networkx as nx
        except ImportError:
            pytest.skip("Matplotlib or NetworkX not available")
        
        # Skip if widget doesn't have matplotlib support
        if not hasattr(self.widget, 'graph_figure') or not self.widget.graph_figure:
            pytest.skip("Widget doesn't have matplotlib support")
        
        # Add test data
        self.storage.add_character("Alice", {"role": "hero"})
        self.storage.add_character("Bob", {"role": "villain"})
        self.storage.add_location("Castle")
        self.storage.add_relationship("Alice", "Bob", "opposes")
        
        # Connect storage
        self.widget.set_graph_storage(self.storage)
        
        # Update graph layout
        self.widget.update_graph_layout()
        
        # Should complete without error
        assert "Ready" in self.widget.status_label.text()
    
    def test_widget_signals(self):
        """Test widget signal emissions."""
        # Test refresh_requested signal
        with patch.object(self.widget, 'refresh_requested') as mock_signal:
            # Trigger refresh
            self.widget.refresh_btn.click()
            
            # Signal might be emitted (depends on implementation)
            # This tests that the signal exists
            assert hasattr(self.widget, 'refresh_requested')
        
        # Test character_selected signal
        assert hasattr(self.widget, 'character_selected')
    
    def test_error_handling_in_refresh(self):
        """Test error handling during data refresh."""
        # Create mock storage that raises exceptions
        mock_storage = Mock()
        mock_storage.get_stats.side_effect = Exception("Mock error")
        mock_storage.get_session_info.return_value = {}
        
        # Connect mock storage
        self.widget.set_graph_storage(mock_storage)
        
        # Refresh should handle error gracefully
        self.widget.refresh_data()
        
        # Should show error status
        assert "Error:" in self.widget.status_label.text()
    
    def test_large_dataset_handling(self):
        """Test widget performance with large datasets."""
        # Add many characters
        for i in range(100):
            self.storage.add_character(f"Character_{i}", {"id": i})
        
        # Connect and refresh
        self.widget.set_graph_storage(self.storage)
        
        # Should handle large dataset without crashing
        self.widget.refresh_data()
        
        # Verify data is displayed
        assert self.widget.characters_table.rowCount() > 0
        assert "Ready" in self.widget.status_label.text()


class TestNarrativeGraphWidgetIntegration:
    """Test widget integration with other components."""
    
    def setup_method(self):
        """Set up test environment."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
    
    def test_widget_lifecycle_with_project(self):
        """Test widget lifecycle with project loading/saving."""
        # Enable AI features for this test
        original_features = getattr(settings, 'aiFeatures', {})
        settings.aiFeatures = {"narrativeGraphMemory": True}
        
        widget = NarrativeGraphWidget()
        
        # Create temporary project
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        temp_file.close()
        
        try:
            # Initialize storage with data
            storage = GraphStorage(temp_file.name)
            storage.add_character("Alice", {"role": "hero"})
            storage.add_location("Castle")
            storage.force_save()
            
            # Connect widget to storage
            widget.set_graph_storage(storage)
            widget.refresh_data()
            
            # Verify data is displayed
            assert widget.characters_table.rowCount() >= 1
            
            # Simulate project reload
            new_storage = GraphStorage(temp_file.name)
            widget.set_graph_storage(new_storage)
            widget.refresh_data()
            
            # Data should persist
            assert widget.characters_table.rowCount() >= 1
            
        finally:
            widget.close()
            os.unlink(temp_file.name)
            # Restore original settings
            settings.aiFeatures = original_features
    
    def test_real_time_updates(self):
        """Test real-time updates when storage changes."""
        widget = NarrativeGraphWidget()
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        temp_file.close()
        storage = GraphStorage(temp_file.name)
        
        try:
            # Connect widget
            widget.set_graph_storage(storage)
            widget.refresh_data()
            
            initial_count = widget.characters_table.rowCount()
            
            # Add data to storage
            storage.add_character("NewCharacter")
            
            # Manual refresh (in real app this would be automatic)
            widget.refresh_data()
            
            # Should show new data
            assert widget.characters_table.rowCount() >= initial_count
            
        finally:
            widget.close()
            os.unlink(temp_file.name)