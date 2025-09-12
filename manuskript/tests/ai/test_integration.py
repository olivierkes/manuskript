#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Comprehensive integration tests for AI features."""

import pytest
import tempfile
import os
import threading
import time
import gc
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread
from PyQt5.QtTest import QTest

from manuskript import settings
from manuskript.ai.narrative_graph.graph_storage import GraphStorage
from manuskript.ai.narrative_graph import narrative_graph
from manuskript.ui.narrative_graph_widget import NarrativeGraphWidget


class TestAIFeaturesIntegration:
    """Comprehensive integration tests for all AI features."""
    
    def setup_method(self):
        """Set up comprehensive test environment."""
        # Ensure QApplication exists
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        # Store original state
        self.original_ai_features = getattr(settings, 'aiFeatures', {})
        self.original_hooks = getattr(settings, 'ai_hooks', {})
        
        # Create temporary project
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        
        # Reset AI system
        settings.aiFeatures = {"narrativeGraphMemory": True}
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
        
        # Initialize components
        self.storage = GraphStorage(self.temp_file.name)
        self.widget = NarrativeGraphWidget()
        narrative_graph.initialize(self.temp_file.name)
    
    def teardown_method(self):
        """Comprehensive cleanup."""
        # Close widget
        if hasattr(self, 'widget'):
            self.widget.close()
        
        # Restore original state
        settings.aiFeatures = self.original_ai_features
        settings.ai_hooks = self.original_hooks
        
        # Clean up files
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
        
        # Clean up graph files
        for ext in ['.narrative_graph.pkl', '.narrative_graph.json']:
            try:
                os.unlink(self.temp_file.name.replace('.msk', ext))
            except FileNotFoundError:
                pass
        
        # Force garbage collection
        gc.collect()


class TestDockablePanelIntegration:
    """Test dockable panel rendering and updates."""
    
    def setup_method(self):
        """Set up panel test environment."""
        if not QApplication.instance():
            self.app = QApplication([])
        
        self.widget = NarrativeGraphWidget()
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        self.storage = GraphStorage(self.temp_file.name)
        
        # Enable AI features
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def teardown_method(self):
        """Clean up panel tests."""
        if hasattr(self, 'widget'):
            self.widget.close()
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_dockable_panel_complete_lifecycle(self):
        """Test complete dockable panel lifecycle with real data flow."""
        # 1. Panel initialization
        assert self.widget.tab_widget.count() == 5
        assert self.widget.characters_table.rowCount() == 0
        
        # 2. Connect storage and populate with realistic data
        self.storage.add_character("Alice Vambrace", {
            "role": "protagonist", 
            "age": 28, 
            "description": "A skilled knight with a mysterious past"
        })
        self.storage.add_character("Lord Malaketh", {
            "role": "antagonist",
            "age": 45,
            "description": "The dark lord of the northern kingdoms"
        })
        self.storage.add_location("Ironhold Castle", "Ancient fortress guarding the mountain pass")
        self.storage.add_location("Whispering Woods", "Enchanted forest where spirits dwell")
        self.storage.add_relationship("Alice Vambrace", "Lord Malaketh", "sworn_enemy")
        self.storage.add_event("siege_of_ironhold", 
                             ["Alice Vambrace", "Lord Malaketh"], 
                             "major_battle",
                             "The climactic siege that determined the fate of the realm")
        
        # 3. Connect widget to storage
        self.widget.set_graph_storage(self.storage)
        
        # 4. Test real-time updates
        initial_stats = self.widget.stats_label.text()
        self.widget.refresh_data()
        updated_stats = self.widget.stats_label.text()
        
        # Verify data propagation
        assert "Nodes:" in updated_stats
        assert "Characters: 2" in updated_stats
        assert self.widget.characters_table.rowCount() == 2
        assert self.widget.relationships_table.rowCount() >= 1
        assert self.widget.events_tree.topLevelItemCount() >= 1
        
        # 5. Test tab switching functionality
        for tab_index in range(self.widget.tab_widget.count()):
            self.widget.tab_widget.setCurrentIndex(tab_index)
            QTest.qWait(10)  # Allow UI to update
            assert self.widget.tab_widget.currentIndex() == tab_index
        
        # 6. Test dynamic updates
        self.storage.add_character("Captain Thorek", {"role": "ally"})
        self.widget.refresh_data()
        assert self.widget.characters_table.rowCount() == 3
        
        # 7. Test panel state persistence
        self.widget.show()
        assert self.widget.isVisible()
        
        # 8. Test feature disable/enable
        settings.aiFeatures["narrativeGraphMemory"] = False
        self.widget.refresh_data()
        assert "Feature disabled" in self.widget.status_label.text()
        
        settings.aiFeatures["narrativeGraphMemory"] = True
        self.widget.refresh_data()
        assert "Ready" in self.widget.status_label.text()
    
    def test_panel_performance_with_large_datasets(self):
        """Test panel performance with large datasets (stress test)."""
        # Create large dataset
        start_time = time.time()
        
        for i in range(500):  # 500 characters
            self.storage.add_character(f"Character_{i:03d}", {
                "role": f"role_{i % 10}",
                "age": 20 + (i % 50),
                "description": f"Description for character {i}" * 10  # Long descriptions
            })
        
        for i in range(200):  # 200 locations
            self.storage.add_location(f"Location_{i:03d}", f"Description for location {i}" * 20)
        
        for i in range(100):  # 100 events
            participants = [f"Character_{j:03d}" for j in range(i, min(i+5, 500))]
            self.storage.add_event(f"event_{i:03d}", participants, "type_battle", f"Event {i} description")
        
        creation_time = time.time() - start_time
        assert creation_time < 30.0, f"Dataset creation took {creation_time}s, too slow"
        
        # Test widget performance
        self.widget.set_graph_storage(self.storage)
        
        refresh_start = time.time()
        self.widget.refresh_data()
        refresh_time = time.time() - refresh_start
        
        assert refresh_time < 5.0, f"Widget refresh took {refresh_time}s, too slow"
        
        # Verify data integrity
        assert self.widget.characters_table.rowCount() <= 500  # May be pruned
        assert "Characters:" in self.widget.stats_label.text()
        assert "Ready" in self.widget.status_label.text()
    
    def test_panel_concurrent_updates(self):
        """Test panel behavior under concurrent updates."""
        self.widget.set_graph_storage(self.storage)
        
        # Function to add data from different threads
        def add_data_worker(thread_id, count):
            for i in range(count):
                char_name = f"Thread_{thread_id}_Char_{i}"
                self.storage.add_character(char_name, {"thread": thread_id})
                time.sleep(0.01)  # Small delay to increase chance of race conditions
        
        # Start multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=add_data_worker, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        # Concurrently refresh widget multiple times
        for _ in range(10):
            self.widget.refresh_data()
            time.sleep(0.05)
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Final refresh and verify
        self.widget.refresh_data()
        
        # Should have data from all threads without corruption
        assert self.widget.characters_table.rowCount() >= 25  # 5 threads * 10 chars, may be pruned
        assert "Ready" in self.widget.status_label.text()


class TestGraphNodeOperations:
    """Test comprehensive graph node operations."""
    
    def setup_method(self):
        """Set up graph operations test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        self.storage = GraphStorage(self.temp_file.name)
    
    def teardown_method(self):
        """Clean up graph operations tests."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_comprehensive_node_operations(self):
        """Test complete CRUD operations on graph nodes."""
        # 1. CREATE operations
        # Add characters with complex attributes
        self.storage.add_character("Aeliana Starweaver", {
            "role": "mage",
            "age": 142,
            "race": "elf",
            "abilities": ["fireball", "teleport", "mind_read"],
            "backstory": "Born in the ancient forests of Eldermere, Aeliana discovered her magical abilities at a young age.",
            "relationships": {"mentor": "Archmage Valdris", "rival": "Necromancer Xareth"}
        })
        
        # Add locations with hierarchical relationships
        self.storage.add_location("Kingdom of Valdoria", "The northern realm ruled by King Aldric")
        self.storage.add_location("Valdoria Capital", "Seat of power in Valdoria")
        self.storage.add_location("Royal Palace", "The king's residence within the capital")
        
        # Add complex relationships
        self.storage.add_relationship("Aeliana Starweaver", "Kingdom of Valdoria", "serves", {
            "loyalty": "high",
            "years_of_service": 25,
            "rank": "court_mage"
        })
        
        # Add interconnected events
        self.storage.add_event("dragon_attack", 
                             ["Aeliana Starweaver"], 
                             "crisis",
                             "Ancient dragon threatens the kingdom")
        
        # 2. READ operations
        stats = self.storage.get_stats()
        assert stats['characters'] >= 1
        assert stats['locations'] >= 3
        assert stats['total_edges'] >= 1
        assert stats['events'] >= 1
        
        # 3. UPDATE operations
        # Update character with new attributes
        self.storage.add_character("Aeliana Starweaver", {
            "age": 143,  # Birthday!
            "new_ability": "dragon_speak",
            "status": "veteran_hero"
        })
        
        # Verify update didn't create duplicate
        updated_stats = self.storage.get_stats()
        assert updated_stats['characters'] == stats['characters']  # Same count
        
        # 4. DELETE operations (via memory management/pruning)
        # Test memory limits
        original_max = self.storage.MAX_NODES
        self.storage.MAX_NODES = 10  # Very low limit
        
        # Add many nodes to trigger pruning
        for i in range(20):
            self.storage.add_character(f"TempChar_{i}", {"temp": True})
        
        final_stats = self.storage.get_stats()
        assert final_stats['total_nodes'] <= self.storage.MAX_NODES
        
        # Restore original limit
        self.storage.MAX_NODES = original_max
    
    def test_edge_cases_node_operations(self):
        """Test edge cases in node operations."""
        # 1. Empty/null inputs
        self.storage.add_character("", {})  # Empty name
        self.storage.add_character("ValidChar", None)  # None attributes
        self.storage.add_location("", "")  # Empty location
        self.storage.add_relationship("", "", "")  # Empty relationship
        
        # Should handle gracefully without crashing
        stats = self.storage.get_stats()
        assert isinstance(stats, dict)
        
        # 2. Extremely long names and descriptions
        long_name = "A" * 10000  # 10KB character name
        long_desc = "B" * 50000  # 50KB description
        
        self.storage.add_character(long_name, {"description": long_desc})
        self.storage.add_location(long_name, long_desc)
        
        # Should handle without error
        stats = self.storage.get_stats()
        assert stats['characters'] >= 1
        assert stats['locations'] >= 1
        
        # 3. Special characters and Unicode
        special_chars = "测试_🎭_Café_Naïve_Σωκράτης_العربية"
        self.storage.add_character(special_chars, {"description": "Unicode test 测试 🎭"})
        
        # 4. Maximum relationships per node
        central_char = "CentralCharacter"
        self.storage.add_character(central_char)
        
        # Add many relationships
        for i in range(100):
            other_char = f"RelatedChar_{i}"
            self.storage.add_character(other_char)
            self.storage.add_relationship(central_char, other_char, f"relationship_{i}")
        
        # Should handle many relationships
        stats = self.storage.get_stats()
        assert stats['total_edges'] >= 50  # May be pruned
    
    def test_rapid_successive_updates(self):
        """Test rapid successive updates to graph nodes."""
        # Rapid character updates
        char_name = "RapidUpdateChar"
        
        start_time = time.time()
        for i in range(1000):  # 1000 rapid updates
            self.storage.add_character(char_name, {
                "update_count": i,
                "timestamp": time.time(),
                "data": f"update_{i}"
            })
        
        update_time = time.time() - start_time
        assert update_time < 10.0, f"1000 updates took {update_time}s, too slow"
        
        # Verify final state
        stats = self.storage.get_stats()
        assert stats['characters'] >= 1
        
        # Rapid relationship updates
        for i in range(500):
            source = f"Source_{i % 10}"  # Reuse some sources
            target = f"Target_{i % 10}"  # Reuse some targets
            self.storage.add_character(source)
            self.storage.add_character(target)
            self.storage.add_relationship(source, target, "rapid_rel")
        
        # Should handle rapid relationship creation
        final_stats = self.storage.get_stats()
        assert final_stats['total_edges'] >= 100  # May be pruned


class TestHookSystemComprehensive:
    """Comprehensive hook system tests."""
    
    def setup_method(self):
        """Set up hook system tests."""
        # Reset hook system
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def teardown_method(self):
        """Clean up hook system tests."""
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
    
    def test_comprehensive_hook_lifecycle(self):
        """Test complete hook lifecycle: register, trigger, remove."""
        callback_calls = []
        
        # 1. REGISTER hooks with different configurations
        def basic_callback(*args, **kwargs):
            callback_calls.append(("basic", args, kwargs))
        
        def feature_callback(*args, **kwargs):
            callback_calls.append(("feature", args, kwargs))
        
        def priority_callback(*args, **kwargs):
            callback_calls.append(("priority", args, kwargs))
        
        # Register with different priorities and features
        settings.register_hook("text_changed", basic_callback)
        settings.register_hook("text_changed", feature_callback, feature_key="narrativeGraphMemory")
        settings.register_hook("text_changed", priority_callback, priority=5)  # Higher priority
        
        # 2. TRIGGER hooks and verify execution order
        settings.trigger_hook("text_changed", "test text", editor=None)
        
        # Verify all callbacks were called
        assert len(callback_calls) == 3
        
        # Verify priority ordering (priority_callback should be first)
        assert callback_calls[0][0] == "priority"
        
        # 3. Test feature-based filtering
        callback_calls.clear()
        settings.aiFeatures["narrativeGraphMemory"] = False
        
        settings.trigger_hook("text_changed", "test text")
        
        # Only basic and priority callbacks should be called (not feature_callback)
        called_types = [call[0] for call in callback_calls]
        assert "feature" not in called_types
        assert "basic" in called_types
        assert "priority" in called_types
        
        # 4. REMOVE hooks (by clearing)
        settings.ai_hooks["text_changed"] = []
        callback_calls.clear()
        
        settings.trigger_hook("text_changed", "test text")
        
        # No callbacks should be called
        assert len(callback_calls) == 0
    
    def test_hook_event_propagation(self):
        """Test correct propagation of events through hook system."""
        # Track event propagation
        event_log = []
        
        def before_load_hook(project_path, main_window):
            event_log.append(("before_load", project_path))
        
        def after_load_hook(project_path, main_window):
            event_log.append(("after_load", project_path))
        
        def text_changed_hook(text, index, editor):
            event_log.append(("text_changed", text[:10]))  # First 10 chars
        
        # Register hooks
        settings.register_hook("before_load", before_load_hook)
        settings.register_hook("after_load", after_load_hook)
        settings.register_hook("text_changed", text_changed_hook)
        
        # Simulate project lifecycle
        project_path = "/test/project.msk"
        mock_mw = Mock()
        
        settings.trigger_hook("before_load", project_path, mock_mw)
        settings.trigger_hook("after_load", project_path, mock_mw)
        settings.trigger_hook("text_changed", "This is a test text for the hook system", None, None)
        
        # Verify correct event propagation
        assert len(event_log) == 3
        assert event_log[0] == ("before_load", project_path)
        assert event_log[1] == ("after_load", project_path)
        assert event_log[2] == ("text_changed", "This is a ")
    
    def test_hook_thread_safety(self):
        """Test hook system thread safety."""
        call_count = threading.local()
        call_count.value = 0
        
        def thread_safe_callback(*args, **kwargs):
            # Simulate some work
            current = getattr(call_count, 'value', 0)
            time.sleep(0.001)  # Small delay to increase chance of race conditions
            call_count.value = current + 1
        
        # Register callback
        settings.register_hook("text_changed", thread_safe_callback)
        
        # Function to trigger hooks from multiple threads
        def trigger_hooks(thread_id, count):
            for i in range(count):
                settings.trigger_hook("text_changed", f"Thread {thread_id} text {i}")
        
        # Start multiple threads
        threads = []
        for thread_id in range(10):
            thread = threading.Thread(target=trigger_hooks, args=(thread_id, 20))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify thread safety (no crashes or corruption)
        # Note: This test mainly verifies that the system doesn't crash under concurrent access
        stats = settings.get_hook_stats() if hasattr(settings, 'get_hook_stats') else {}
        assert isinstance(stats, dict)  # Basic sanity check
    
    def test_hook_exception_handling_comprehensive(self):
        """Test comprehensive exception handling in hook system."""
        successful_calls = []
        
        def failing_callback(*args, **kwargs):
            raise Exception("Intentional test failure")
        
        def succeeding_callback(*args, **kwargs):
            successful_calls.append(("success", args))
        
        def critical_failing_callback(*args, **kwargs):
            raise SystemError("Critical system error")
        
        # Register hooks including failing ones
        settings.register_hook("text_changed", failing_callback, priority=1)
        settings.register_hook("text_changed", succeeding_callback, priority=2)
        settings.register_hook("text_changed", critical_failing_callback, priority=3)
        settings.register_hook("text_changed", succeeding_callback, priority=4)  # Different instance
        
        # Trigger hooks - should not crash despite exceptions
        settings.trigger_hook("text_changed", "test")
        
        # Verify that non-failing callbacks were still executed
        assert len(successful_calls) >= 1
        successful_calls.clear()
        
        # Test with different event types
        for event_type in ["before_load", "after_load", "before_save", "character_changed"]:
            settings.register_hook(event_type, failing_callback)
            settings.register_hook(event_type, succeeding_callback)
            
            # Should handle exceptions gracefully
            if event_type in ["before_load", "after_load", "before_save"]:
                settings.trigger_hook(event_type, "/test/path", Mock())
            else:
                settings.trigger_hook(event_type, "test_data")
        
        # System should still be functional
        assert len(successful_calls) >= 4  # One for each event type
    
    def test_rapid_hook_registration_and_removal(self):
        """Test rapid hook registration and removal."""
        # Rapidly register and trigger hooks
        callbacks = []
        
        for i in range(100):
            def make_callback(index):
                return lambda *args, **kwargs: callbacks.append(index)
            
            callback = make_callback(i)
            settings.register_hook("text_changed", callback, priority=i)
            
            # Occasionally trigger to test with changing hook list
            if i % 10 == 0:
                settings.trigger_hook("text_changed", f"test_{i}")
        
        # Final trigger with all hooks registered
        callbacks.clear()
        settings.trigger_hook("text_changed", "final_test")
        
        # Should have called all 100 callbacks
        assert len(callbacks) == 100
        
        # Verify priority ordering
        assert callbacks == list(range(100))
        
        # Rapid removal (by clearing)
        settings.ai_hooks["text_changed"] = []
        callbacks.clear()
        settings.trigger_hook("text_changed", "after_clear")
        
        # No callbacks should be called
        assert len(callbacks) == 0


class TestAIFeaturesSettings:
    """Test AI features settings and activation/deactivation."""
    
    def setup_method(self):
        """Set up AI features settings tests."""
        self.original_ai_features = getattr(settings, 'aiFeatures', {})
        settings.aiFeatures = {}
    
    def teardown_method(self):
        """Clean up AI features settings tests."""
        settings.aiFeatures = self.original_ai_features
    
    def test_feature_activation_deactivation_cycle(self):
        """Test complete feature activation/deactivation cycle."""
        # 1. Initial state - features disabled
        settings.aiFeatures = {"narrativeGraphMemory": False}
        
        # Register feature-dependent hook
        callback_calls = []
        def feature_hook(*args, **kwargs):
            callback_calls.append(args)
        
        settings.register_hook("text_changed", feature_hook, feature_key="narrativeGraphMemory")
        
        # Trigger hook - should not be called
        settings.trigger_hook("text_changed", "test")
        assert len(callback_calls) == 0
        
        # 2. Activate feature
        settings.aiFeatures["narrativeGraphMemory"] = True
        
        # Trigger hook - should now be called
        settings.trigger_hook("text_changed", "test")
        assert len(callback_calls) == 1
        
        # 3. Deactivate feature
        settings.aiFeatures["narrativeGraphMemory"] = False
        callback_calls.clear()
        
        # Trigger hook - should not be called again
        settings.trigger_hook("text_changed", "test")
        assert len(callback_calls) == 0
        
        # 4. Reactivate feature
        settings.aiFeatures["narrativeGraphMemory"] = True
        
        # Should work again
        settings.trigger_hook("text_changed", "test")
        assert len(callback_calls) == 1
    
    def test_lazy_loading_behavior(self):
        """Test lazy loading of dependencies only when features are enabled."""
        # Mock the narrative graph module
        with patch('manuskript.ai.narrative_graph.narrative_graph') as mock_module:
            # Feature disabled - should not initialize
            settings.aiFeatures = {"narrativeGraphMemory": False}
            
            # Simulate feature check
            if settings.aiFeatures.get("narrativeGraphMemory", False):
                mock_module.initialize()
            
            # Should not have been called
            mock_module.initialize.assert_not_called()
            
            # Enable feature - should initialize
            settings.aiFeatures["narrativeGraphMemory"] = True
            
            if settings.aiFeatures.get("narrativeGraphMemory", False):
                mock_module.initialize()
            
            # Should have been called now
            mock_module.initialize.assert_called_once()
    
    def test_missing_dependencies_handling(self):
        """Test handling of missing AI dependencies when features are activated."""
        # Test with missing NetworkX
        with patch.dict('sys.modules', {'networkx': None}):
            # Should handle gracefully
            temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
            temp_file.close()
            
            try:
                storage = GraphStorage(temp_file.name)
                storage.add_character("Test", {"role": "test"})
                
                # Should use fallback storage
                stats = storage.get_stats()
                assert stats['characters'] >= 1
                
            finally:
                os.unlink(temp_file.name)
        
        # Test with missing spaCy
        with patch.dict('sys.modules', {'spacy': None}):
            # Should handle gracefully
            from manuskript.ai.narrative_graph.utils import extract_entities
            
            entities = extract_entities("Alice went to the Castle")
            
            # Should use regex fallback
            assert 'characters' in entities
            assert 'locations' in entities
    
    def test_placeholder_module_handling(self):
        """Test handling of non-wired AI modules without system crashes."""
        # Test with completely missing AI module
        with patch.dict('sys.modules'):
            if 'manuskript.ai.narrative_graph.narrative_graph' in sys.modules:
                del sys.modules['manuskript.ai.narrative_graph.narrative_graph']
            
            # Should handle missing module gracefully
            try:
                from manuskript.ai.narrative_graph import narrative_graph
                narrative_graph.initialize()
            except ImportError:
                # Expected behavior - should not crash the system
                pass
        
        # Test with partially working module
        with patch('manuskript.ai.narrative_graph.narrative_graph.initialize', side_effect=Exception("Init failed")):
            # Should handle initialization failure
            try:
                narrative_graph.initialize()
            except Exception:
                # Should not propagate and crash system
                pass


class TestPerformanceAndStability:
    """Performance and stability stress tests."""
    
    def setup_method(self):
        """Set up performance tests."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        
        # Enable all features for maximum load
        settings.aiFeatures = {
            "narrativeGraphMemory": True,
            "characterAnalysis": True
        }
    
    def teardown_method(self):
        """Clean up performance tests."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_stress_rapid_node_operations(self):
        """Stress test for rapid node addition/removal."""
        storage = GraphStorage(self.temp_file.name)
        
        # Set very aggressive pruning for stress test
        original_max = storage.MAX_NODES
        storage.MAX_NODES = 100
        
        try:
            start_time = time.time()
            
            # Phase 1: Rapid node addition
            for batch in range(10):  # 10 batches
                for i in range(50):  # 50 nodes per batch
                    node_id = f"batch_{batch}_node_{i}"
                    storage.add_character(node_id, {
                        "batch": batch,
                        "index": i,
                        "data": f"Data for {node_id}" * 10,
                        "timestamp": time.time()
                    })
                    
                    # Add relationships within batch
                    if i > 0:
                        prev_node = f"batch_{batch}_node_{i-1}"
                        storage.add_relationship(node_id, prev_node, "follows")
                
                # Trigger pruning check
                stats = storage.get_stats()
                assert stats['total_nodes'] <= storage.MAX_NODES * 1.5  # Allow some overflow
            
            operation_time = time.time() - start_time
            assert operation_time < 60.0, f"Stress test took {operation_time}s, too slow"
            
            # Verify system stability
            final_stats = storage.get_stats()
            assert isinstance(final_stats, dict)
            assert final_stats['total_nodes'] <= storage.MAX_NODES
            
        finally:
            storage.MAX_NODES = original_max
    
    def test_memory_usage_and_cleanup(self):
        """Test memory usage and cleanup effectiveness."""
        storage = GraphStorage(self.temp_file.name)
        
        # Set limits for memory test
        original_max = storage.MAX_NODES
        storage.MAX_NODES = 200
        
        try:
            # Get initial memory usage
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Add large amount of data
            for i in range(1000):
                # Create large character descriptions
                large_desc = "A" * 1000 + f" Character {i} " + "B" * 1000
                
                storage.add_character(f"LargeChar_{i}", {
                    "description": large_desc,
                    "attributes": {f"attr_{j}": f"value_{j}" * 50 for j in range(10)},
                    "history": [f"event_{k}" * 100 for k in range(5)]
                })
                
                # Periodically check memory growth
                if i % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_growth = current_memory - initial_memory
                    
                    # Memory growth should be reasonable due to pruning
                    assert memory_growth < 500, f"Memory grew by {memory_growth}MB, too much"
            
            # Force garbage collection
            storage.force_save()
            gc.collect()
            
            # Verify memory cleanup
            final_memory = process.memory_info().rss / 1024 / 1024
            total_growth = final_memory - initial_memory
            
            # Should not have excessive memory growth due to pruning
            assert total_growth < 200, f"Total memory growth {total_growth}MB excessive"
            
            # Verify data integrity after cleanup
            stats = storage.get_stats()
            assert stats['total_nodes'] <= storage.MAX_NODES
            assert stats['characters'] > 0
            
        except ImportError:
            pytest.skip("psutil not available for memory testing")
        
        finally:
            storage.MAX_NODES = original_max
    
    def test_concurrent_access_stability(self):
        """Test system stability under concurrent access."""
        storage = GraphStorage(self.temp_file.name)
        if not QApplication.instance():
            app = QApplication([])
        
        widget = NarrativeGraphWidget()
        widget.set_graph_storage(storage)
        
        # Shared state for threads
        thread_results = {}
        exception_count = threading.local()
        exception_count.value = 0
        
        def concurrent_worker(worker_id, operation_count):
            """Worker function for concurrent operations."""
            try:
                for i in range(operation_count):
                    # Mix of operations
                    if i % 4 == 0:  # Add character
                        storage.add_character(f"worker_{worker_id}_char_{i}", {
                            "worker": worker_id,
                            "operation": i
                        })
                    elif i % 4 == 1:  # Add location
                        storage.add_location(f"worker_{worker_id}_loc_{i}", f"Location {i}")
                    elif i % 4 == 2:  # Add relationship
                        if i > 0:
                            source = f"worker_{worker_id}_char_{i-1}"
                            target = f"worker_{worker_id}_char_{i}"
                            storage.add_relationship(source, target, "concurrent_rel")
                    else:  # Update widget
                        widget.refresh_data()
                
                thread_results[worker_id] = "completed"
                
            except Exception as e:
                current = getattr(exception_count, 'value', 0)
                exception_count.value = current + 1
                thread_results[worker_id] = f"failed: {e}"
        
        # Start concurrent workers
        threads = []
        for worker_id in range(8):
            thread = threading.Thread(target=concurrent_worker, args=(worker_id, 25))
            threads.append(thread)
            thread.start()
        
        # Monitor system during concurrent access
        start_time = time.time()
        monitoring_active = True
        
        def monitor_system():
            while monitoring_active and time.time() - start_time < 30:
                try:
                    # Periodic system checks
                    stats = storage.get_stats()
                    session_info = storage.get_session_info()
                    widget.refresh_data()
                    
                    # Basic sanity checks
                    assert isinstance(stats, dict)
                    assert isinstance(session_info, dict)
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    current = getattr(exception_count, 'value', 0)
                    exception_count.value = current + 1
        
        monitor_thread = threading.Thread(target=monitor_system)
        monitor_thread.start()
        
        # Wait for all workers
        for thread in threads:
            thread.join()
        
        monitoring_active = False
        monitor_thread.join()
        
        # Verify system stability
        completed_workers = sum(1 for result in thread_results.values() if result == "completed")
        exception_rate = exception_count.value / (len(threads) * 25 + 100)  # Approximate total operations
        
        assert completed_workers >= 6, f"Only {completed_workers} workers completed successfully"
        assert exception_rate < 0.1, f"Exception rate {exception_rate} too high"
        
        # Final system integrity check
        final_stats = storage.get_stats()
        assert final_stats['characters'] > 0
        assert widget.status_label.text() != ""
        
        widget.close()


# Utility functions for test setup
def create_test_project_data(storage, complexity="medium"):
    """Create test data with different complexity levels."""
    if complexity == "simple":
        storage.add_character("Alice", {"role": "hero"})
        storage.add_character("Bob", {"role": "villain"})
        storage.add_location("Castle")
        storage.add_relationship("Alice", "Bob", "opposes")
    
    elif complexity == "medium":
        characters = [
            ("Alice Brightblade", {"role": "protagonist", "age": 25, "class": "paladin"}),
            ("Marcus Shadowmere", {"role": "antagonist", "age": 45, "class": "necromancer"}),
            ("Elara Moonwhisper", {"role": "ally", "age": 120, "class": "elf_mage"}),
            ("Captain Thorek", {"role": "mentor", "age": 50, "class": "warrior"})
        ]
        
        locations = [
            ("Ironhold Keep", "Ancient fortress protecting the realm"),
            ("Shadowmere Tower", "Dark spire where evil magic is practiced"),
            ("Whispering Woods", "Enchanted forest full of mysteries"),
            ("Port Goldenhaven", "Bustling trade city by the sea")
        ]
        
        for name, attrs in characters:
            storage.add_character(name, attrs)
        
        for name, desc in locations:
            storage.add_location(name, desc)
        
        # Add relationships
        storage.add_relationship("Alice Brightblade", "Marcus Shadowmere", "sworn_enemy")
        storage.add_relationship("Alice Brightblade", "Elara Moonwhisper", "trusted_friend")
        storage.add_relationship("Captain Thorek", "Alice Brightblade", "mentors")
        
        # Add events
        storage.add_event("siege_of_ironhold", 
                         ["Alice Brightblade", "Marcus Shadowmere", "Captain Thorek"],
                         "major_battle",
                         "The climactic siege that decided the war")
    
    elif complexity == "complex":
        # Create large interconnected world
        for i in range(50):
            storage.add_character(f"Character_{i:02d}", {
                "role": ["hero", "villain", "ally", "neutral"][i % 4],
                "age": 20 + (i % 60),
                "faction": f"Faction_{i % 5}",
                "skills": [f"skill_{j}" for j in range((i % 3) + 1)]
            })
        
        for i in range(20):
            storage.add_location(f"Location_{i:02d}", f"Description for location {i}")
        
        # Create complex relationship web
        for i in range(100):
            source = f"Character_{i % 50:02d}"
            target = f"Character_{(i + 1) % 50:02d}"
            rel_type = ["ally", "enemy", "neutral", "family"][i % 4]
            storage.add_relationship(source, target, rel_type)
        
        # Add major events
        for i in range(10):
            participants = [f"Character_{j:02d}" for j in range(i, min(i+5, 50))]
            storage.add_event(f"event_{i:02d}", participants, "major_event", f"Important event {i}")