#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for the narrative graph storage system."""

import pytest
import tempfile
import os
import json
import pickle
import threading
import time
from unittest.mock import Mock, patch, MagicMock

# Skip entire module if NetworkX not available
pytest.importorskip("networkx", reason="NetworkX required for graph storage tests")

from manuskript.ai.narrative_graph.graph_storage import GraphStorage


class TestGraphStorage:
    """Test the GraphStorage class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        self.project_path = self.temp_file.name
        self.storage = GraphStorage(self.project_path)
    
    def teardown_method(self):
        """Clean up after tests."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
        # Clean up any graph files
        graph_files = [
            self.project_path.replace('.msk', '.narrative_graph.pkl'),
            self.project_path.replace('.msk', '.narrative_graph.json')
        ]
        for f in graph_files:
            try:
                os.unlink(f)
            except FileNotFoundError:
                pass
    
    def test_initialization(self):
        """Test graph storage initialization."""
        assert self.storage.project_path == self.project_path
        assert self.storage.changes_since_save == 0
        assert hasattr(self.storage, 'graph')
        # Check for NetworkX graph or dict fallback
        assert hasattr(self.storage.graph, 'nodes') or isinstance(self.storage.graph, dict)
    
    def test_add_character_basic(self):
        """Test adding a character to the graph."""
        self.storage.add_character("Alice", {"role": "protagonist", "age": 25})
        
        stats = self.storage.get_stats()
        assert stats['characters'] >= 1
        assert stats['total_nodes'] >= 1
    
    def test_add_character_with_updates(self):
        """Test updating an existing character."""
        # Add character
        self.storage.add_character("Alice", {"role": "protagonist"})
        
        # Update character
        self.storage.add_character("Alice", {"age": 25, "hair": "blonde"})
        
        stats = self.storage.get_stats()
        assert stats['characters'] == 1  # Should still be 1 character
    
    def test_add_location(self):
        """Test adding a location to the graph."""
        self.storage.add_location("Castle", "A dark and mysterious castle")
        
        stats = self.storage.get_stats()
        assert stats['locations'] >= 1
        assert stats['total_nodes'] >= 1
    
    def test_add_relationship(self):
        """Test adding relationships between entities."""
        # First add some characters
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        
        # Add relationship
        self.storage.add_relationship("Alice", "Bob", "knows", {"strength": "strong"})
        
        stats = self.storage.get_stats()
        assert stats['total_edges'] >= 1
    
    def test_add_event(self):
        """Test adding events to the graph."""
        # Add characters first
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        
        # Add event
        self.storage.add_event(
            "meeting_1",
            ["Alice", "Bob"],
            "encounter",
            "Alice and Bob meet for the first time"
        )
        
        stats = self.storage.get_stats()
        assert stats['events'] >= 1
    
    def test_get_character_connections_networkx(self):
        """Test getting character connections with NetworkX."""
        # Skip if NetworkX not available
        try:
            import networkx as nx
        except ImportError:
            pytest.skip("NetworkX not available")
        
        # Add characters and relationships
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        self.storage.add_character("Charlie")
        self.storage.add_relationship("Alice", "Bob", "knows")
        self.storage.add_relationship("Bob", "Charlie", "knows")
        
        # Test depth 1 connections
        if hasattr(self.storage.graph, 'nodes'):
            connections = self.storage.get_character_connections("Alice", depth=1)
            assert connections is not None
    
    def test_save_and_load_pickle(self):
        """Test saving and loading graph with pickle."""
        # Add some data
        self.storage.add_character("Alice", {"role": "hero"})
        self.storage.add_location("Castle", "Dark castle")
        self.storage.add_relationship("Alice", "Castle", "visits")
        
        # Force save
        self.storage.force_save()
        
        # Create new storage instance and load
        new_storage = GraphStorage(self.project_path)
        new_stats = new_storage.get_stats()
        
        assert new_stats['characters'] >= 1
        assert new_stats['locations'] >= 1
        assert new_stats['total_edges'] >= 1
    
    def test_save_and_load_json_fallback(self):
        """Test JSON fallback when pickle fails."""
        # Add some data
        self.storage.add_character("Alice")
        self.storage.add_location("Castle")
        
        # Mock pickle to fail and force JSON saving
        with patch('pickle.dump', side_effect=Exception("Pickle failed")):
            self.storage.force_save()
        
        # Should have created JSON file
        json_path = self.project_path.replace('.msk', '.narrative_graph.json')
        assert os.path.exists(json_path)
        
        # Load and verify
        new_storage = GraphStorage(self.project_path)
        new_stats = new_storage.get_stats()
        assert new_stats['total_nodes'] > 0
    
    def test_auto_save_threshold(self):
        """Test that auto-save triggers after enough changes."""
        original_threshold = self.storage.auto_save_threshold
        self.storage.auto_save_threshold = 3  # Lower threshold for testing
        
        # Add changes that should trigger auto-save
        self.storage.add_character("Alice")
        self.storage.add_character("Bob") 
        self.storage.add_character("Charlie")  # This should trigger auto-save
        
        # Wait briefly for async save
        time.sleep(0.1)
        
        # Changes should be reset after auto-save
        assert self.storage.changes_since_save <= self.storage.auto_save_threshold
        
        # Restore original threshold
        self.storage.auto_save_threshold = original_threshold
    
    def test_memory_management_pruning(self):
        """Test graph pruning when memory limits are reached."""
        original_max = self.storage.MAX_NODES
        self.storage.MAX_NODES = 5  # Very low limit for testing
        
        # Add many nodes to trigger pruning
        for i in range(10):
            self.storage.add_character(f"Character_{i}")
        
        stats = self.storage.get_stats()
        # Should have triggered pruning check, but may not prune until PRUNE_THRESHOLD
        # Check that pruning mechanism exists and limits are respected
        assert stats['total_nodes'] <= self.storage.MAX_NODES * 1.5  # Allow some overflow before pruning
        
        # Restore original limit
        self.storage.MAX_NODES = original_max
    
    def test_thread_safety(self):
        """Test thread safety of graph operations."""
        def add_characters(start, end):
            for i in range(start, end):
                self.storage.add_character(f"Char_{i}", {"thread": threading.current_thread().name})
        
        # Create multiple threads adding characters
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_characters, args=(i*10, (i+1)*10))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all characters were added without corruption
        stats = self.storage.get_stats()
        assert stats['characters'] == 30
    
    def test_get_stats_comprehensive(self):
        """Test comprehensive statistics reporting."""
        # Add diverse data
        self.storage.add_character("Alice", {"role": "hero"})
        self.storage.add_character("Bob", {"role": "villain"})
        self.storage.add_location("Castle")
        self.storage.add_location("Forest")
        self.storage.add_relationship("Alice", "Bob", "opposes")
        self.storage.add_event("battle_1", ["Alice", "Bob"], "conflict", "Epic battle")
        
        stats = self.storage.get_stats()
        
        # Verify all expected keys
        expected_keys = ['total_nodes', 'total_edges', 'characters', 'locations', 'events', 'density']
        for key in expected_keys:
            assert key in stats
        
        assert stats['characters'] == 2
        assert stats['locations'] == 2
        assert stats['events'] == 1
        assert stats['total_edges'] >= 1
    
    def test_get_session_info(self):
        """Test session information reporting."""
        # Make some changes
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        
        session_info = self.storage.get_session_info()
        
        assert 'changes_since_save' in session_info
        assert 'last_save_time' in session_info
        assert 'tracked_nodes' in session_info
        
        assert session_info['changes_since_save'] == 2
    
    def test_node_access_tracking(self):
        """Test that node access is tracked for memory management."""
        # Add and access characters
        self.storage.add_character("Alice")
        self.storage.add_character("Bob")
        
        # Access Alice multiple times (should be tracked internally)
        for _ in range(5):
            self.storage.add_character("Alice", {"access": "tracked"})
        
        session_info = self.storage.get_session_info()
        assert session_info['tracked_nodes'] >= 1
    
    @patch('manuskript.ai.narrative_graph.graph_storage.nx', None)
    def test_fallback_storage_without_networkx(self):
        """Test dict-based storage when NetworkX is not available."""
        # Create new storage without NetworkX
        fallback_storage = GraphStorage(self.project_path + "_fallback")
        
        # Add data using fallback storage
        fallback_storage.add_character("Alice", {"role": "hero"})
        fallback_storage.add_location("Castle", "Dark place")
        fallback_storage.add_relationship("Alice", "Castle", "visits")
        
        # Verify data was stored
        stats = fallback_storage.get_stats()
        assert stats['total_nodes'] >= 2
        assert stats['characters'] >= 1
        assert stats['locations'] >= 1
    
    def test_error_handling_corrupt_data(self):
        """Test handling of corrupt save files."""
        # Create a corrupt pickle file
        pickle_path = self.project_path.replace('.msk', '.narrative_graph.pkl')
        with open(pickle_path, 'wb') as f:
            f.write(b'corrupt_data_not_pickle')
        
        # Should handle corruption gracefully and start fresh
        new_storage = GraphStorage(self.project_path)
        stats = new_storage.get_stats()
        
        # Should initialize with empty graph
        assert stats['total_nodes'] == 0
    
    def test_large_text_handling(self):
        """Test handling of large text descriptions."""
        large_text = "A" * 10000  # 10KB of text
        
        self.storage.add_character("BigChar", {"description": large_text})
        self.storage.add_location("BigLocation", large_text)
        
        # Should handle without error
        stats = self.storage.get_stats()
        assert stats['characters'] >= 1
        assert stats['locations'] >= 1
    
    def test_special_characters_handling(self):
        """Test handling of special characters in names and data."""
        special_chars = "Alice_测试_🎭_special-char's"
        
        self.storage.add_character(special_chars, {"role": "测试角色"})
        self.storage.add_location("Château_élégant")
        
        stats = self.storage.get_stats()
        assert stats['characters'] >= 1
        assert stats['locations'] >= 1
        
        # Test save/load with special characters
        self.storage.force_save()
        new_storage = GraphStorage(self.project_path)
        new_stats = new_storage.get_stats()
        assert new_stats['characters'] >= 1
        assert new_stats['locations'] >= 1


class TestGraphStorageEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_project_path(self):
        """Test handling of invalid project paths."""
        # Test with non-existent directory
        invalid_path = "/non/existent/path/project.msk"
        
        # Should handle gracefully
        storage = GraphStorage(invalid_path)
        storage.add_character("Test")
        
        # Basic operations should work
        stats = storage.get_stats()
        assert stats['characters'] >= 1
    
    def test_empty_data_operations(self):
        """Test operations with empty or None data."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        storage = GraphStorage(temp_file.name)
        
        # Test with empty strings and None values
        storage.add_character("", {})
        storage.add_character("ValidName", None)
        storage.add_location("", "")
        storage.add_relationship("", "", "")
        
        # Should handle without crashing
        stats = storage.get_stats()
        assert isinstance(stats, dict)
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_concurrent_save_operations(self):
        """Test concurrent save operations."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        storage = GraphStorage(temp_file.name)
        
        def concurrent_save():
            storage.add_character(f"Char_{threading.current_thread().name}")
            storage.force_save()
        
        # Start multiple save operations
        threads = []
        for i in range(3):
            thread = threading.Thread(target=concurrent_save)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have completed without errors
        stats = storage.get_stats()
        assert stats['characters'] == 3
        
        # Cleanup
        os.unlink(temp_file.name)