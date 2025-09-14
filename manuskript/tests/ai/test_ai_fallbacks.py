#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""
Tests for AI feature fallbacks.

These tests verify that the AI features work even when optional dependencies
are not installed, using fallback implementations.
"""

import pytest
from unittest.mock import patch, MagicMock
from manuskript import settings


class TestAIFallbacks:
    """Test that AI features work with fallback implementations."""
    
    def setup_method(self):
        """Set up test environment."""
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def test_narrative_graph_without_networkx(self):
        """Test narrative graph with NetworkX mocked out."""
        with patch.dict('sys.modules', {'networkx': None}):
            # Should use dictionary fallback
            from manuskript.ai.narrative_graph.graph_storage import GraphStorage
            import tempfile
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
            storage = GraphStorage(temp_file.name)
            
            # Should work with basic dictionary
            storage.add_character("Alice")
            stats = storage.get_stats()
            assert stats['characters'] >= 1
    
    def test_entity_extraction_without_spacy(self):
        """Test entity extraction falls back when spaCy unavailable."""
        with patch('manuskript.ai.narrative_graph.utils.get_nlp_model', return_value=None):
            from manuskript.ai.narrative_graph.utils import extract_entities
            
            # Should use NLTK or regex fallback
            text = "Alice visited the Castle."
            entities = extract_entities(text)
            
            assert 'characters' in entities
            assert 'locations' in entities
            assert 'Alice' in entities['characters']
    
    def test_hook_system_always_works(self):
        """Test that hook system works regardless of AI dependencies."""
        # Hook system has no external dependencies
        called = []
        
        def test_hook(text):
            called.append(text)
        
        settings.register_hook("text_changed", test_hook)
        settings.trigger_hook("text_changed", "test")
        
        assert "test" in called
    
    def test_ai_features_can_be_disabled(self):
        """Test that AI features can be completely disabled."""
        settings.aiFeatures = {"narrativeGraphMemory": False}
        
        # Should not process when disabled
        called = []
        
        def test_hook(text):
            called.append(text)
        
        settings.register_hook("text_changed", test_hook, feature_key="narrativeGraphMemory")
        settings.trigger_hook("text_changed", "test")
        
        # Should not be called when feature is disabled
        assert len(called) == 0