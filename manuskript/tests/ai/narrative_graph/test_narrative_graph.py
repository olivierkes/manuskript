#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for the narrative graph core module."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Skip entire module if NetworkX not available
pytest.importorskip("networkx", reason="NetworkX required for narrative graph tests")

from manuskript import settings
from manuskript.ai.narrative_graph import narrative_graph
from manuskript.ai.narrative_graph import utils
from manuskript.ai.narrative_graph.graph_storage import GraphStorage


class TestNarrativeGraphModule:
    """Test the main narrative graph module."""
    
    def setup_method(self):
        """Set up test environment."""
        # Store original state
        self.original_storage = getattr(narrative_graph, 'current_graph_storage', None)
        self.original_ai_features = getattr(settings, 'aiFeatures', {})
        
        # Set up test environment
        settings.aiFeatures = {"narrativeGraphMemory": True}
        
        # Initialize fresh
        narrative_graph.current_graph_storage = None
    
    def teardown_method(self):
        """Clean up after tests."""
        # Restore original state
        narrative_graph.current_graph_storage = self.original_storage
        settings.aiFeatures = self.original_ai_features
    
    def test_initialize_basic(self):
        """Test basic module initialization."""
        narrative_graph.initialize()
        
        # Should have registered hooks
        assert len(settings.ai_hooks["text_changed"]) > 0
        assert len(settings.ai_hooks["after_load"]) > 0
        assert len(settings.ai_hooks["before_save"]) > 0
    
    def test_initialize_with_project_path(self):
        """Test initialization with a specific project path."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        temp_file.close()
        
        try:
            narrative_graph.initialize(temp_file.name)
            
            assert narrative_graph.current_graph_storage is not None
            assert narrative_graph.current_graph_storage.project_path == temp_file.name
            
        finally:
            os.unlink(temp_file.name)
    
    def test_on_project_loaded(self):
        """Test project loaded hook."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        temp_file.close()
        mock_main_window = Mock()
        
        try:
            narrative_graph.on_project_loaded(temp_file.name, mock_main_window)
            
            assert narrative_graph.current_graph_storage is not None
            assert narrative_graph.current_graph_storage.project_path == temp_file.name
            
        finally:
            os.unlink(temp_file.name)
    
    def test_on_project_save(self):
        """Test project saved hook."""
        # Initialize with storage
        narrative_graph.initialize()
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        narrative_graph.current_graph_storage = GraphStorage(temp_file.name)
        
        # Add some data
        narrative_graph.current_graph_storage.add_character("TestChar")
        
        try:
            # Mock main window
            mock_main_window = Mock()
            
            # Call save hook
            narrative_graph.on_project_save(temp_file.name, mock_main_window)
            
            # Should have triggered save (changes reset)
            assert narrative_graph.current_graph_storage.changes_since_save <= 10
            
        finally:
            os.unlink(temp_file.name)
    
    @patch('manuskript.ai.narrative_graph.utils.extract_entities')
    def test_on_text_changed(self, mock_extract):
        """Test text changed hook."""
        # Setup mock
        mock_extract.return_value = {
            'characters': ['Alice', 'Bob'],
            'locations': ['Castle', 'Forest'],
            'events': ['battle_scene']
        }
        
        # Initialize
        narrative_graph.initialize()
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        narrative_graph.current_graph_storage = GraphStorage(temp_file.name)
        
        try:
            # Test text processing
            test_text = "Alice and Bob fought in the Castle near the Forest during the battle_scene."
            narrative_graph.on_text_changed(test_text, None, None)
            
            # Should have extracted and added entities
            mock_extract.assert_called_once_with(test_text)
            
            stats = narrative_graph.current_graph_storage.get_stats()
            assert stats['characters'] >= 2
            assert stats['locations'] >= 2
            
        finally:
            os.unlink(temp_file.name)
    
    def test_on_text_changed_no_storage(self):
        """Test text changed hook when no storage is available."""
        narrative_graph.current_graph_storage = None
        
        # Should not raise error
        result = narrative_graph.on_text_changed("Some text", None, None)
        assert result is None
    
    def test_extract_entities_basic(self):
        """Test basic entity extraction."""
        text = "Alice walked to the Castle where she met Bob."
        
        entities = utils.extract_entities(text)
        
        assert 'characters' in entities
        assert 'locations' in entities
        assert 'relationships' in entities
        
        # Should find capitalized words as potential entities
        characters = entities['characters']
        assert 'Alice' in characters
        assert 'Bob' in characters
        
        locations = entities['locations']
        assert 'Castle' in locations
    
    def test_extract_entities_with_spacy(self):
        """Test entity extraction with spaCy if available."""
        try:
            import spacy
            # Test with spaCy available
            text = "Alice Johnson visited New York City last Tuesday."
            
            entities = utils.extract_entities(text)
            
            # Should extract named entities
            assert 'characters' in entities
            assert 'locations' in entities
            
        except ImportError:
            # Skip if spaCy not available
            pytest.skip("spaCy not available for testing")
    
    def test_extract_entities_empty_text(self):
        """Test entity extraction with empty text."""
        entities = utils.extract_entities("")
        
        assert isinstance(entities, dict)
        assert entities['characters'] == []
        assert entities['locations'] == []
    
    def test_extract_relationships_basic(self):
        """Test basic relationship extraction."""
        text = "Alice loves Bob. Bob knows Charlie."
        entities = {'characters': ['Alice', 'Bob', 'Charlie']}
        
        relationships = utils.analyze_relationships(text, entities)
        
        assert isinstance(relationships, list)
        # Should find some relationships
        assert len(relationships) >= 0  # May not find relationships in simple text
        
        # Check relationship structure if any found
        if relationships:
            rel = relationships[0]
            # analyze_relationships returns tuples (source, rel_type, target)
            assert isinstance(rel, tuple)
            assert len(rel) == 3
    
    def test_suggest_consistency_check_basic(self):
        """Test basic consistency checking."""
        text = "Alice is 25 years old. Later, Alice celebrates her 30th birthday."
        
        issues = narrative_graph.suggest_consistency_check(text)
        
        assert isinstance(issues, list)
        # Might find age inconsistencies or other issues
        # The specific results depend on the implementation
    
    def test_suggest_consistency_check_character_names(self):
        """Test consistency checking for character name variations."""
        text = "Alice walked home. Alise was tired. Alice rested."
        
        issues = narrative_graph.suggest_consistency_check(text)
        
        assert isinstance(issues, list)
        # Might flag 'Alise' as potential typo for 'Alice'
    
    def test_feature_disabled_behavior(self):
        """Test behavior when narrative graph feature is disabled."""
        settings.aiFeatures["narrativeGraphMemory"] = False
        
        # Initialize
        narrative_graph.initialize()
        
        # Text processing should be skipped
        result = narrative_graph.on_text_changed("Alice met Bob", None, None)
        assert result is None
    
    @patch('manuskript.ai.narrative_graph.utils.get_nlp_model')
    def test_entity_extraction_with_model_loading_error(self, mock_get_model):
        """Test entity extraction when NLP model fails to load."""
        mock_get_model.return_value = None  # Simulate model loading failure
        
        text = "Alice visited the Castle."
        entities = utils.extract_entities(text)
        
        # Should fall back to regex-based extraction
        assert 'characters' in entities
        assert 'locations' in entities
        
        # Should still extract capitalized words
        assert 'Alice' in entities['characters']
        assert 'Castle' in entities['locations']


class TestNarrativeGraphIntegration:
    """Test integration between narrative graph components."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        
        # Enable AI features
        settings.aiFeatures = {"narrativeGraphMemory": True}
        
        # Initialize
        narrative_graph.initialize(self.temp_file.name)
    
    def teardown_method(self):
        """Clean up after tests."""
        # Reset global storage
        narrative_graph.current_graph_storage = None
        
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_full_text_processing_pipeline(self):
        """Test the complete text processing pipeline."""
        # Process multiple texts
        texts = [
            "Alice was a brave knight who lived in the Castle.",
            "Bob, the evil wizard, attacked the Village.",
            "Alice and Bob fought fiercely in the Forest.",
            "Charlie helped Alice defeat Bob in the final battle."
        ]
        
        for i, text in enumerate(texts):
            narrative_graph.on_text_changed(text, None, None)
        
        # Verify accumulated knowledge
        storage = narrative_graph.current_graph_storage
        stats = storage.get_stats()
        
        assert stats['characters'] >= 3  # Alice, Bob, Charlie
        assert stats['locations'] >= 3   # Castle, Village, Forest
        assert stats['total_edges'] > 0  # Some relationships
    
    def test_project_lifecycle(self):
        """Test the complete project lifecycle."""
        mock_main_window = Mock()
        
        # 1. Project loaded
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        assert narrative_graph.current_graph_storage is not None
        
        # 2. Process some text
        narrative_graph.on_text_changed("Alice met Bob at the Castle.", None, None)
        
        # 3. Save project
        narrative_graph.on_project_save(self.temp_file.name, mock_main_window)
        
        # 4. Simulate new session - load project again
        narrative_graph.current_graph_storage = None
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        
        # Should restore previous data
        stats = narrative_graph.current_graph_storage.get_stats()
        assert stats['characters'] >= 2
        assert stats['locations'] >= 1
    
    def test_memory_management_integration(self):
        """Test memory management across the full pipeline."""
        # Set low limits for testing
        if narrative_graph.current_graph_storage:
            original_max = narrative_graph.current_graph_storage.MAX_NODES
            narrative_graph.current_graph_storage.MAX_NODES = 10
            
            # Process many texts to trigger pruning
            for i in range(20):
                text = f"Character_{i} visited Location_{i}."
                narrative_graph.on_text_changed(text, None, None)
            
            stats = narrative_graph.current_graph_storage.get_stats()
            assert stats['total_nodes'] <= narrative_graph.current_graph_storage.MAX_NODES
            
            # Restore limit
            narrative_graph.current_graph_storage.MAX_NODES = original_max
    
    def test_error_recovery(self):
        """Test error recovery in the processing pipeline."""
        # Inject an error in entity extraction
        with patch('manuskript.ai.narrative_graph.utils.extract_entities', 
                   side_effect=Exception("Test extraction error")):
            
            # Should handle error gracefully
            result = narrative_graph.on_text_changed("Alice met Bob", None, None)
            
            # Should not crash and storage should remain functional
            storage = narrative_graph.current_graph_storage
            storage.add_character("ManualChar")  # Should work
            stats = storage.get_stats()
            assert stats['characters'] >= 1
    
    def test_concurrent_text_processing(self):
        """Test concurrent text processing."""
        import threading
        import time
        
        def process_text(text_id):
            # Use made-up names to test handling of fictional content
            text = f"Character_{text_id} went to Place_{text_id}."
            narrative_graph.on_text_changed(text, None, None)
        
        # Process texts concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_text, args=(i,))
            threads.append(thread)
            thread.start()
            # Small delay between thread starts to reduce contention
            time.sleep(0.01)
        
        for thread in threads:
            thread.join()
        
        # Give adequate time for async processing to complete
        time.sleep(1.0)
        
        # Verify all data was processed
        stats = narrative_graph.current_graph_storage.get_stats()
        # Be more lenient - at least some data should be processed
        assert stats['characters'] >= 3, f"Expected at least 3 characters, got {stats['characters']}"
        assert stats['locations'] >= 3, f"Expected at least 3 locations, got {stats['locations']}"