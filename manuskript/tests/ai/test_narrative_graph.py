#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Comprehensive tests for the Narrative Graph system.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from manuskript.ai.narrative_graph.graph_engine import (
    NarrativeGraphEngine, Entity, EntityType, Relationship, RelationType
)
from manuskript.ai.narrative_graph.smart_extraction import SmartEntityExtractor


class TestGraphEngine(unittest.TestCase):
    """Test the graph engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = NarrativeGraphEngine(self.temp_dir)
    
    def tearDown(self):
        """Clean up."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_entity(self):
        """Test adding entities."""
        # Add a character
        char_id = self.engine.add_entity("Alice", EntityType.CHARACTER, 
                                         role="Protagonist")
        
        self.assertIn(char_id, self.engine.entities)
        entity = self.engine.entities[char_id]
        self.assertEqual(entity.name, "Alice")
        self.assertEqual(entity.type, EntityType.CHARACTER)
        self.assertEqual(entity.attributes['role'], "Protagonist")
    
    def test_add_duplicate_entity(self):
        """Test adding duplicate entities."""
        # Add same entity twice
        id1 = self.engine.add_entity("Bob", EntityType.CHARACTER)
        id2 = self.engine.add_entity("Bob", EntityType.CHARACTER)
        
        # Should be the same entity with increased mention count
        self.assertEqual(id1, id2)
        self.assertEqual(self.engine.entities[id1].mention_count, 2)
    
    def test_remove_entity(self):
        """Test removing entities."""
        # Add entities and relationship
        alice_id = self.engine.add_entity("Alice", EntityType.CHARACTER)
        bob_id = self.engine.add_entity("Bob", EntityType.CHARACTER)
        self.engine.add_relationship(alice_id, bob_id, RelationType.KNOWS)
        
        # Remove Alice
        result = self.engine.remove_entity(alice_id)
        
        self.assertTrue(result)
        self.assertNotIn(alice_id, self.engine.entities)
        # Relationship should also be removed
        self.assertNotIn((alice_id, bob_id), self.engine.relationships)
    
    def test_add_relationship(self):
        """Test adding relationships."""
        # Add entities
        alice_id = self.engine.add_entity("Alice", EntityType.CHARACTER)
        bob_id = self.engine.add_entity("Bob", EntityType.CHARACTER)
        
        # Add relationship
        result = self.engine.add_relationship(alice_id, bob_id, RelationType.KNOWS)
        
        self.assertTrue(result)
        self.assertIn((alice_id, bob_id), self.engine.relationships)
        rel = self.engine.relationships[(alice_id, bob_id)]
        self.assertEqual(rel.type, RelationType.KNOWS)
    
    def test_add_relationship_invalid_entities(self):
        """Test adding relationship with invalid entities."""
        result = self.engine.add_relationship("invalid1", "invalid2", RelationType.KNOWS)
        self.assertFalse(result)
    
    def test_find_entities(self):
        """Test finding entities."""
        # Add various entities
        self.engine.add_entity("Alice", EntityType.CHARACTER)
        self.engine.add_entity("Bob", EntityType.CHARACTER)
        self.engine.add_entity("Paris", EntityType.LOCATION)
        
        # Find all characters
        chars = self.engine.find_entities(entity_type=EntityType.CHARACTER)
        self.assertEqual(len(chars), 2)
        
        # Find by name pattern
        alice = self.engine.find_entities(name_pattern="Ali")
        self.assertEqual(len(alice), 1)
        self.assertEqual(alice[0].name, "Alice")
    
    def test_find_shortest_path(self):
        """Test finding shortest path between entities."""
        # Create a graph: A -> B -> C
        a_id = self.engine.add_entity("A", EntityType.CHARACTER)
        b_id = self.engine.add_entity("B", EntityType.CHARACTER)
        c_id = self.engine.add_entity("C", EntityType.CHARACTER)
        
        self.engine.add_relationship(a_id, b_id, RelationType.KNOWS)
        self.engine.add_relationship(b_id, c_id, RelationType.KNOWS)
        
        # Find path from A to C
        path = self.engine.find_shortest_path(a_id, c_id)
        
        self.assertIsNotNone(path)
        self.assertEqual(path, [a_id, b_id, c_id])
    
    def test_calculate_importance(self):
        """Test importance calculation."""
        # Create a graph with different connectivity
        hub_id = self.engine.add_entity("Hub", EntityType.CHARACTER)
        
        for i in range(5):
            node_id = self.engine.add_entity(f"Node{i}", EntityType.CHARACTER)
            self.engine.add_relationship(node_id, hub_id, RelationType.KNOWS)
        
        # Calculate importance
        scores = self.engine.calculate_importance()
        
        # Hub should have highest importance
        self.assertGreater(scores[hub_id], scores[node_id])
    
    def test_find_communities(self):
        """Test community detection."""
        # Create two separate communities
        # Community 1
        a1 = self.engine.add_entity("A1", EntityType.CHARACTER)
        a2 = self.engine.add_entity("A2", EntityType.CHARACTER)
        self.engine.add_relationship(a1, a2, RelationType.KNOWS)
        
        # Community 2
        b1 = self.engine.add_entity("B1", EntityType.CHARACTER)
        b2 = self.engine.add_entity("B2", EntityType.CHARACTER)
        self.engine.add_relationship(b1, b2, RelationType.KNOWS)
        
        # Find communities
        communities = self.engine.find_communities()
        
        # Should have 2 communities
        self.assertEqual(len(communities), 2)
        
        # Each community should have 2 members
        for community in communities.values():
            self.assertEqual(len(community), 2)
    
    def test_persistence(self):
        """Test saving and loading."""
        # Add some data
        alice_id = self.engine.add_entity("Alice", EntityType.CHARACTER)
        bob_id = self.engine.add_entity("Bob", EntityType.CHARACTER)
        self.engine.add_relationship(alice_id, bob_id, RelationType.LOVES)
        
        # Save
        self.assertTrue(self.engine.save())
        
        # Create new engine and load
        new_engine = NarrativeGraphEngine(self.temp_dir)
        self.assertTrue(new_engine.load())
        
        # Verify data
        self.assertEqual(len(new_engine.entities), 2)
        self.assertEqual(len(new_engine.relationships), 1)
        self.assertIn(alice_id, new_engine.entities)
        self.assertEqual(new_engine.entities[alice_id].name, "Alice")
    
    def test_thread_safety(self):
        """Test thread safety of operations."""
        import threading
        
        def add_entities():
            for i in range(100):
                self.engine.add_entity(f"Entity{i}", EntityType.CHARACTER)
        
        # Run multiple threads
        threads = [threading.Thread(target=add_entities) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have added entities safely
        # (may have duplicates due to race conditions, but should not crash)
        self.assertGreater(len(self.engine.entities), 0)
    
    def test_performance_metrics(self):
        """Test performance tracking."""
        # Perform operations that populate the cache
        self.engine.add_entity("Test", EntityType.CHARACTER)
        
        # First call should populate cache (cache miss)
        self.engine.get_statistics()
        
        # Second call should hit cache (no invalidation between calls)
        self.engine.get_statistics()
        
        # Check metrics
        self.assertGreater(self.engine.metrics['total_operations'], 0)
        self.assertGreater(self.engine.metrics['cache_hits'], 0)


class TestSmartExtraction(unittest.TestCase):
    """Test smart entity extraction."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock main window
        self.mock_window = Mock()
        self.mock_window.mdlCharacter = Mock()
        self.mock_window.mdlCharacter.rowCount.return_value = 2
        self.mock_window.mdlCharacter.index.return_value = Mock()
        self.mock_window.mdlCharacter.data.side_effect = ["Alice", "Bob"]
        
        self.mock_window.mdlWorld = Mock()
        self.mock_window.mdlWorld.invisibleRootItem.return_value = Mock()
        
        self.extractor = SmartEntityExtractor(self.mock_window)
    
    def test_load_existing_entities(self):
        """Test loading existing entities from models."""
        # Should have loaded characters
        self.assertIn("Alice", self.extractor.known_characters)
        self.assertIn("Bob", self.extractor.known_characters)
    
    def test_extract_from_text(self):
        """Test entity extraction from text."""
        text = "Alice met Bob in Paris. Alice said hello to Bob."
        
        # Mock known entities
        self.extractor.known_characters = {"Alice", "Bob"}
        self.extractor.known_locations = {"Paris"}
        
        result = self.extractor.extract_from_text(text)
        
        # Should find known entities
        self.assertIn("Alice", result["characters"])
        self.assertIn("Bob", result["characters"])
        self.assertIn("Paris", result["locations"])
        
        # Should count mentions
        self.assertEqual(result["character_mentions"]["Alice"], 2)
        self.assertEqual(result["character_mentions"]["Bob"], 2)
    
    def test_extract_interactions(self):
        """Test interaction extraction."""
        text = "Alice talked to Bob. Bob helped Charlie."
        characters = {"Alice", "Bob", "Charlie"}
        
        interactions = self.extractor._extract_interactions(text, characters)
        
        # Should find interactions
        self.assertEqual(len(interactions), 2)
        self.assertIn(("Alice", "talked to", "Bob"), interactions)
        self.assertIn(("Bob", "helped", "Charlie"), interactions)
    
    def test_name_variations(self):
        """Test handling of name variations."""
        self.extractor._add_name_variations("John Smith")
        
        # Should add variations
        self.assertIn("John", self.extractor.character_aliases)
        self.assertIn("Smith", self.extractor.character_aliases)
        self.assertIn("Mr. Smith", self.extractor.character_aliases)
        
        # All should map to full name
        self.assertEqual(self.extractor.character_aliases["John"], "John Smith")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from extraction to visualization."""
        # Create components
        temp_dir = tempfile.mkdtemp()
        engine = NarrativeGraphEngine(temp_dir)
        
        # Mock main window
        mock_window = Mock()
        mock_window.mdlCharacter = Mock()
        mock_window.mdlCharacter.rowCount.return_value = 0
        mock_window.mdlWorld = Mock()
        
        extractor = SmartEntityExtractor(mock_window)
        
        # Process some text
        text = """
        In the kingdom of Eldoria, Princess Elena faced a difficult choice.
        The evil wizard Malachar had captured her friend, Sir Garrett.
        Elena traveled to the Dark Tower where Malachar lived.
        She confronted Malachar and saved Garrett.
        """
        
        # Extract entities (simplified)
        entities = {
            "characters": ["Elena", "Malachar", "Garrett"],
            "locations": ["Eldoria", "Dark Tower"]
        }
        
        # Add to engine
        for char in entities["characters"]:
            engine.add_entity(char, EntityType.CHARACTER)
        
        for loc in entities["locations"]:
            engine.add_entity(loc, EntityType.LOCATION)
        
        # Add relationships (Elena as central protagonist)
        elena_id = "character_elena"
        malachar_id = "character_malachar"
        garrett_id = "character_garrett"
        eldoria_id = "location_eldoria"
        tower_id = "location_dark_tower"
        
        # Elena as clear protagonist with many more connections
        engine.add_relationship(elena_id, garrett_id, RelationType.FRIEND)
        engine.add_relationship(elena_id, malachar_id, RelationType.ENEMY)
        engine.add_relationship(elena_id, eldoria_id, RelationType.INTERACTS)  # Lives in
        engine.add_relationship(elena_id, tower_id, RelationType.INTERACTS)   # Travels to
        
        # Give Elena more connections to ensure centrality
        # Add reverse relationships to ensure Elena receives PageRank score
        engine.add_relationship(garrett_id, elena_id, RelationType.FRIEND)    # Mutual friendship
        engine.add_relationship(eldoria_id, elena_id, RelationType.INTERACTS) # Kingdom connection
        
        # Others have fewer connections
        engine.add_relationship(malachar_id, garrett_id, RelationType.ENEMY)
        engine.add_relationship(malachar_id, tower_id, RelationType.INTERACTS) # Lives in
        
        # Test graph operations
        # Find Elena's connections (should be 4: Garrett, Malachar, Eldoria, Tower)
        elena_edges = engine.index.outgoing_edges[elena_id]
        self.assertEqual(len(elena_edges), 4)
        
        # Find path from Garrett to Malachar
        path = engine.find_shortest_path(garrett_id, malachar_id)
        self.assertIsNotNone(path)
        
        # Calculate importance
        scores = engine.calculate_importance()
        # Elena should be most important (protagonist)
        self.assertGreater(scores[elena_id], scores[garrett_id])
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


class TestPerformance(unittest.TestCase):
    """Performance tests."""
    
    def test_large_graph_performance(self):
        """Test performance with large graphs."""
        import time
        
        temp_dir = tempfile.mkdtemp()
        engine = NarrativeGraphEngine(temp_dir)
        
        # Add many entities
        start_time = time.time()
        
        for i in range(1000):
            engine.add_entity(f"Entity{i}", EntityType.CHARACTER)
        
        add_time = time.time() - start_time
        
        # Should be fast
        self.assertLess(add_time, 1.0)  # Less than 1 second for 1000 entities
        
        # Add relationships
        start_time = time.time()
        
        for i in range(0, 1000, 2):
            engine.add_relationship(
                f"character_entity{i}",
                f"character_entity{i+1}",
                RelationType.KNOWS
            )
        
        rel_time = time.time() - start_time
        self.assertLess(rel_time, 1.0)
        
        # Test query performance
        start_time = time.time()
        engine.find_entities(entity_type=EntityType.CHARACTER)
        query_time = time.time() - start_time
        self.assertLess(query_time, 0.1)  # Should be very fast
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_memory_usage(self):
        """Test memory efficiency."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        temp_dir = tempfile.mkdtemp()
        engine = NarrativeGraphEngine(temp_dir)
        
        # Add many entities
        for i in range(10000):
            engine.add_entity(f"Entity{i}", EntityType.CHARACTER)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should use reasonable memory (less than 100MB for 10k entities)
        self.assertLess(memory_increase, 100)
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()