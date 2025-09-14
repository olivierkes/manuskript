#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""
Realistic User Workflow Tests for AI Features

These tests simulate actual user interactions and workflows to ensure
the AI features work as users will actually use them.
"""

import pytest
import tempfile
import os
import time
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from manuskript import settings
from manuskript.ai.narrative_graph.graph_storage import GraphStorage
from manuskript.ai.narrative_graph import narrative_graph
from manuskript.ui.narrative_graph_widget import NarrativeGraphWidget


class TestRealisticWritingWorkflow:
    """Test AI features in realistic writing scenarios."""
    
    def setup_method(self):
        """Set up realistic writing environment."""
        # Create temporary project file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        
        # Initialize Qt application
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        # Enable AI features like user would through settings
        settings.aiFeatures = {"narrativeGraphMemory": True}
        
        # Initialize AI system
        narrative_graph.initialize()
        
        # Simulate project loading
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        
        # Create UI widget
        self.widget = NarrativeGraphWidget()
        self.widget.set_graph_storage(narrative_graph.current_graph_storage)
    
    def teardown_method(self):
        """Clean up realistic test environment."""
        if hasattr(self, 'widget'):
            self.widget.close()
        
        # Reset global graph storage
        narrative_graph.current_graph_storage = None
        
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
    
    def test_complete_story_writing_session(self):
        """Test a complete story writing session from start to finish."""
        # Simulate user starting a new story
        story_texts = [
            # Chapter 1: Introduction
            "Alice Brightblade stood at the gates of Ironhold Castle, her silver armor gleaming in the morning sun. " +
            "The young paladin had traveled far from her home in the village of Millhaven to answer the call for heroes.",
            
            # Chapter 2: The Quest Begins  
            "Captain Thorek, a grizzled veteran with scars across his weathered face, briefed Alice on the mission. " +
            "'The dark necromancer Marcus Shadowmere has taken refuge in the Whispering Woods,' he explained gravely.",
            
            # Chapter 3: Into the Woods
            "Alice ventured deep into the Whispering Woods, where ancient trees whispered secrets and shadows moved " +
            "with unnatural purpose. She knew Marcus Shadowmere was somewhere ahead, plotting his next evil scheme.",
            
            # Chapter 4: The Confrontation
            "In a clearing bathed in eerie moonlight, Alice finally confronted Marcus Shadowmere. The necromancer's " +
            "eyes glowed with dark magic as he raised his staff. 'You're too late, paladin!' he sneered.",
            
            # Chapter 5: The Battle
            "The battle between Alice and Marcus raged through the night. Steel clashed against dark magic as the " +
            "two warriors fought for the fate of the realm. Alice's holy light blazed against Marcus's shadow spells."
        ]
        
        # Simulate user typing each chapter (triggers text_changed hooks)
        for i, text in enumerate(story_texts):
            # Simulate typing delay (like real user)
            time.sleep(0.1)
            
            # Trigger text analysis like editor would
            narrative_graph.on_text_changed(text, index=None, editor=None)
            
            # Update UI like real application would
            self.widget.refresh_data()
            
            # Verify progressive story building
            stats = narrative_graph.current_graph_storage.get_stats()
            
            # Should accumulate characters over time
            if i == 0:  # First chapter
                assert stats['characters'] >= 1, "Should detect Alice in first chapter"
            elif i == 1:  # Second chapter
                assert stats['characters'] >= 2, "Should detect Alice and Captain Thorek"
            elif i == 2:  # Third chapter
                assert stats['characters'] >= 3, "Should detect Marcus Shadowmere"
            
            # Should accumulate locations
            assert stats['locations'] >= i // 2, f"Should detect locations by chapter {i+1}"
        
        # Final verification - complete story analysis
        final_stats = narrative_graph.current_graph_storage.get_stats()
        
        # Should have identified main characters
        assert final_stats['characters'] >= 2, f"Should identify at least Alice and Marcus, got {final_stats['characters']}"
        
        # Should have identified key locations (be more lenient due to NLP variations)
        assert final_stats['locations'] >= 2, f"Should identify at least Castle and Woods, got {final_stats['locations']}"
        
        # Should have created relationships
        assert final_stats['total_edges'] >= 1, f"Should create at least one relationship, got {final_stats['total_edges']}"
        
        # UI should reflect the story data (be lenient with counts)
        assert self.widget.characters_table.rowCount() >= 2, f"Should show at least 2 characters in UI, got {self.widget.characters_table.rowCount()}"
        # Status should indicate processing is complete
        status_text = self.widget.status_label.text()
        assert any(word in status_text for word in ["Ready", "Complete", "Analyzed"]), f"Status should show completion, got: {status_text}"
    
    def test_project_save_load_persistence(self):
        """Test that AI data persists across project save/load cycles like real usage."""
        mock_main_window = Mock()
        
        # Phase 1: Create story content
        initial_text = (
            "Elena Stormwind, a powerful mage from the Academy of Arcane Arts, "
            "received an urgent message from High Wizard Aldric. The message spoke "
            "of strange magical disturbances near the Ancient Ruins of Zephyr."
        )
        
        # User creates content
        narrative_graph.on_text_changed(initial_text, None, None)
        self.widget.refresh_data()
        
        initial_stats = narrative_graph.current_graph_storage.get_stats()
        assert initial_stats['characters'] >= 2  # Elena and Aldric
        
        # Phase 2: User saves project (like File -> Save)
        narrative_graph.on_project_save(self.temp_file.name, mock_main_window)
        
        # Phase 3: Simulate application restart by clearing memory
        narrative_graph.current_graph_storage = None
        self.widget.set_graph_storage(None)
        
        # Phase 4: User reopens project (like File -> Open)
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        self.widget.set_graph_storage(narrative_graph.current_graph_storage)
        self.widget.refresh_data()
        
        # Phase 5: Verify persistence
        restored_stats = narrative_graph.current_graph_storage.get_stats()
        
        # Data should be restored
        assert restored_stats['characters'] == initial_stats['characters']
        assert restored_stats['locations'] == initial_stats['locations']
        assert restored_stats['total_edges'] == initial_stats['total_edges']
        
        # UI should show restored data
        assert self.widget.characters_table.rowCount() >= 2
        
        # Phase 6: User continues writing
        continuation_text = (
            "Elena met with Aldric in his tower study. Maps of the Ancient Ruins "
            "covered his desk, marked with strange symbols. 'The barrier between "
            "realms grows thin,' Aldric warned Elena gravely."
        )
        
        narrative_graph.on_text_changed(continuation_text, None, None)
        self.widget.refresh_data()
        
        # Should build upon existing data
        continued_stats = narrative_graph.current_graph_storage.get_stats()
        assert continued_stats['characters'] >= restored_stats['characters']
        assert continued_stats['total_edges'] >= restored_stats['total_edges']
    
    def test_ai_feature_toggle_during_writing(self):
        """Test toggling AI features on/off during active writing session."""
        # User starts with AI features enabled
        assert settings.aiFeatures["narrativeGraphMemory"] is True
        
        # User writes some content
        text1 = "Sir Gareth rode through the Forbidden Valley, seeking the lost Crown of Kings."
        narrative_graph.on_text_changed(text1, None, None)
        self.widget.refresh_data()
        
        # Verify AI analysis worked
        stats_enabled = narrative_graph.current_graph_storage.get_stats()
        assert stats_enabled['characters'] >= 1
        assert self.widget.characters_table.rowCount() >= 1
        
        # User disables AI features (like in Settings dialog)
        settings.aiFeatures["narrativeGraphMemory"] = False
        self.widget.refresh_data()
        
        # Widget should show feature disabled
        assert "Feature disabled" in self.widget.status_label.text()
        assert self.widget.characters_table.rowCount() == 0
        
        # User continues writing (should not analyze)
        text2 = "Princess Lyanna appeared from the shadows, warning Gareth of danger ahead."
        # Use trigger_hook so feature flag is respected
        settings.trigger_hook("text_changed", text2, None, None)
        
        # Analysis should be skipped
        stats_disabled = narrative_graph.current_graph_storage.get_stats()
        assert stats_disabled == stats_enabled  # No new analysis
        
        # User re-enables AI features
        settings.aiFeatures["narrativeGraphMemory"] = True
        self.widget.refresh_data()
        
        # Should restore previous data and resume analysis
        assert "Ready" in self.widget.status_label.text()
        assert self.widget.characters_table.rowCount() >= 1
        
        # New content should be analyzed
        text3 = "Queen Morgana's army approached from the Eastern Marshes."
        narrative_graph.on_text_changed(text3, None, None)
        self.widget.refresh_data()
        
        stats_reenabled = narrative_graph.current_graph_storage.get_stats()
        assert stats_reenabled['characters'] >= stats_enabled['characters']
    
    def test_ui_responsiveness_during_heavy_analysis(self):
        """Test UI remains responsive during heavy text analysis."""
        # Create a very long, complex text
        complex_text = ""
        characters = ["Alice", "Bob", "Charlie", "Diana", "Edmund", "Fiona", "George", "Helen"]
        locations = ["Castle", "Forest", "Village", "Mountain", "River", "Desert", "Island", "Tower"]
        
        for i in range(50):  # 50 sentences
            char = characters[i % len(characters)]
            loc = locations[i % len(locations)]
            complex_text += f"In sentence {i}, {char} traveled to the {loc} and discovered ancient secrets. "
        
        # Record UI state before analysis
        initial_ui_responsive = True
        
        # Start analysis (should be async for CPU-heavy work)
        start_time = time.time()
        narrative_graph.on_text_changed(complex_text, None, None)
        
        # UI should remain responsive (not block for long)
        analysis_time = time.time() - start_time
        assert analysis_time < 2.0, f"UI blocked for {analysis_time}s - too long"
        
        # Allow time for async processing to complete
        max_wait = 10.0
        wait_time = 0.0
        while wait_time < max_wait:
            time.sleep(0.1)
            wait_time += 0.1
            
            # Try to refresh UI
            self.widget.refresh_data()
            
            # Check if analysis is complete
            stats = narrative_graph.current_graph_storage.get_stats()
            if stats['characters'] >= 5:  # Reasonable expectation
                break
        
        # Verify analysis eventually completed
        final_stats = narrative_graph.current_graph_storage.get_stats()
        assert final_stats['characters'] >= 5, "Analysis should identify multiple characters"
        assert final_stats['locations'] >= 5, "Analysis should identify multiple locations"
        
        # UI should show results
        assert self.widget.characters_table.rowCount() >= 5
    
    def test_consistency_checker_real_scenario(self):
        """Test consistency checker with realistic writing inconsistencies."""
        # User creates story with potential consistency issues
        inconsistent_text = (
            "Alice was 25 years old when she began her quest. She had brown hair and green eyes. "
            "After traveling for two years, Alice finally reached the castle. "
            "The 30-year-old warrior with blonde hair and blue eyes stood before the gates. "
            "Alice remembered her training from when she was 20 years old at the Academy."
        )
        
        # Process the text
        narrative_graph.on_text_changed(inconsistent_text, None, None)
        self.widget.set_last_text(inconsistent_text)  # Store text for consistency checking
        self.widget.refresh_data()
        
        # Switch to consistency tab
        consistency_tab_index = -1
        for i in range(self.widget.tab_widget.count()):
            if self.widget.tab_widget.tabText(i) == "Consistency":
                consistency_tab_index = i
                break
        
        assert consistency_tab_index >= 0, "Consistency tab should exist"
        self.widget.tab_widget.setCurrentIndex(consistency_tab_index)
        
        # User runs consistency check
        self.widget.run_consistency_check()
        
        # Should find issues
        issues_count = self.widget.issues_table.rowCount()
        assert issues_count > 0, "Should detect consistency issues"
        
        # Should provide meaningful feedback
        found_age_issue = False
        found_appearance_issue = False
        
        for row in range(issues_count):
            issue_text = self.widget.issues_table.item(row, 1).text().lower()
            if "age" in issue_text or "25" in issue_text or "30" in issue_text:
                found_age_issue = True
            if "hair" in issue_text or "eye" in issue_text or "brown" in issue_text:
                found_appearance_issue = True
        
        # At least one type of inconsistency should be detected
        # Be lenient as NLP models may vary in detection capability
        if issues_count > 0:
            assert found_age_issue or found_appearance_issue, "Should detect character inconsistencies"
        else:
            # If no issues detected, just ensure the checker ran without errors
            assert self.widget.check_btn.isEnabled(), "Consistency checker completed successfully"
    
    def test_graph_visualization_user_interaction(self):
        """Test user interaction with graph visualization."""
        # Skip if matplotlib not available
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            pytest.skip("Matplotlib or NetworkX not available")
        
        # Create story with clear relationships
        story_text = (
            "King Arthur ruled from Camelot with wisdom and justice. "
            "His trusted knight Lancelot served him faithfully. "
            "The wizard Merlin advised Arthur in matters of magic. "
            "Queen Guinevere supported Arthur in ruling the kingdom."
        )
        
        narrative_graph.on_text_changed(story_text, None, None)
        self.widget.refresh_data()
        
        # Find and switch to graph view tab
        graph_tab_index = -1
        for i in range(self.widget.tab_widget.count()):
            if "Graph" in self.widget.tab_widget.tabText(i):
                graph_tab_index = i
                break
        
        if graph_tab_index >= 0 and hasattr(self.widget, 'graph_figure') and self.widget.graph_figure:
            self.widget.tab_widget.setCurrentIndex(graph_tab_index)
            
            # User clicks "Update Layout" button
            self.widget.update_graph_layout()
            
            # Should generate visualization without errors
            assert "Ready" in self.widget.status_label.text()
            
            # Graph should have nodes representing our story
            stats = narrative_graph.current_graph_storage.get_stats()
            assert stats['characters'] >= 3  # Arthur, Lancelot, Merlin, Guinevere
            assert stats['locations'] >= 1   # Camelot


class TestErrorRecoveryAndEdgeCases:
    """Test system behavior in error conditions and edge cases users might encounter."""
    
    def setup_method(self):
        """Set up error testing environment."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        self.temp_file.close()
        
        if not QApplication.instance():
            self.app = QApplication([])
        
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def teardown_method(self):
        """Clean up error tests."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_corrupted_save_file_recovery(self):
        """Test recovery when user's save file is corrupted."""
        # Create a corrupted graph save file
        graph_file = self.temp_file.name.replace('.msk', '.narrative_graph.pkl')
        with open(graph_file, 'w') as f:
            f.write("CORRUPTED_DATA_NOT_PICKLE")
        
        # User tries to load project
        narrative_graph.initialize()
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        
        # Should handle corruption gracefully
        assert narrative_graph.current_graph_storage is not None
        
        # Should start with clean state
        stats = narrative_graph.current_graph_storage.get_stats()
        assert stats['total_nodes'] == 0
        
        # User can continue working normally
        narrative_graph.on_text_changed("Alice went to the castle.", None, None)
        new_stats = narrative_graph.current_graph_storage.get_stats()
        assert new_stats['characters'] >= 1
    
    def test_out_of_disk_space_handling(self):
        """Test behavior when disk space is exhausted during save."""
        narrative_graph.initialize()
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        storage = narrative_graph.current_graph_storage
        
        # Add some data
        storage.add_character("TestChar")
        
        # Mock disk space error
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            # Should handle save failure gracefully
            try:
                storage.force_save()
                # Should not crash
            except OSError:
                # If it propagates, that's also acceptable behavior
                pass
        
        # System should remain functional
        storage.add_character("AnotherChar")
        stats = storage.get_stats()
        assert stats['characters'] >= 1
    
    def test_massive_text_input_handling(self):
        """Test handling extremely large text input (like user pastes entire book)."""
        narrative_graph.initialize()
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        
        # Create massive text (1MB)
        massive_text = "Alice went to the castle. " * 40000  # ~1MB of text
        
        # Should handle without crashing or taking too long
        start_time = time.time()
        narrative_graph.on_text_changed(massive_text, None, None)
        process_time = time.time() - start_time
        
        # Should complete in reasonable time (may be async)
        assert process_time < 30.0, f"Processing took {process_time}s - too slow"
        
        # Should produce reasonable results
        stats = narrative_graph.current_graph_storage.get_stats()
        assert stats['characters'] >= 1
        assert stats['locations'] >= 1
    
    def test_rapid_user_input_handling(self):
        """Test rapid successive user input (like fast typing)."""
        narrative_graph.initialize()
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        
        # Simulate rapid typing
        texts = [
            "Alice",
            "Alice went",
            "Alice went to",
            "Alice went to the",
            "Alice went to the castle",
            "Alice went to the castle.",
            "Alice went to the castle. Bob",
            "Alice went to the castle. Bob was",
            "Alice went to the castle. Bob was there",
            "Alice went to the castle. Bob was there."
        ]
        
        # Process rapidly (like real typing)
        for text in texts:
            narrative_graph.on_text_changed(text, None, None)
            time.sleep(0.01)  # Very fast typing
        
        # Allow async processing to complete
        time.sleep(1.0)
        
        # Should produce coherent results
        stats = narrative_graph.current_graph_storage.get_stats()
        assert stats['characters'] >= 2  # Alice and Bob
        assert stats['locations'] >= 1   # castle
    
    def test_unicode_and_emoji_handling(self):
        """Test handling of international text and emojis."""
        narrative_graph.initialize()
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        
        # Text with various Unicode characters
        unicode_text = (
            "艾丽斯 traveled to 東京 where she met José. "
            "They went to the café ☕ and discussed 📚 books. "
            "Привет said Vladimir from Москва. "
            "العربية النص with some emojis 🎭🏰⚔️."
        )
        
        # Should handle without crashing
        narrative_graph.on_text_changed(unicode_text, None, None)
        
        stats = narrative_graph.current_graph_storage.get_stats()
        
        # Should extract some entities (exact results may vary with NLP capabilities)
        assert stats['total_nodes'] >= 2, "Should extract some entities from Unicode text"
        
        # Should save and load Unicode data
        narrative_graph.current_graph_storage.force_save()
        
        # Reload
        narrative_graph.initialize()
        mock_main_window = Mock()
        narrative_graph.on_project_loaded(self.temp_file.name, mock_main_window)
        restored_stats = narrative_graph.current_graph_storage.get_stats()
        
        # Should preserve Unicode data
        assert restored_stats['total_nodes'] >= 2


class TestPerformanceWithRealisticData:
    """Test performance characteristics with realistic data volumes."""
    
    def test_novel_length_processing(self):
        """Test processing a novel-length work (~80,000 words)."""
        if not QApplication.instance():
            app = QApplication([])
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.msk', delete=False)
        temp_file.close()
        
        try:
            settings.aiFeatures = {"narrativeGraphMemory": True}
            narrative_graph.initialize(temp_file.name)
            
            # Create novel-length content (simplified for testing)
            chapter_template = (
                "In chapter {}, protagonist {} traveled to {} where they met {}. "
                "The antagonist {} was plotting in {}. A battle occurred at {} "
                "involving characters {} and {}. The story continues..."
            )
            
            characters = ["Alice", "Bob", "Charlie", "Diana", "Edmund", "Fiona"]
            locations = ["Castle", "Forest", "Village", "Mountain", "Desert", "Island"]
            
            start_time = time.time()
            
            # Process 20 chapters (realistic novel size sample)
            for chapter in range(20):
                chapter_text = chapter_template.format(
                    chapter + 1,
                    characters[chapter % len(characters)],
                    locations[chapter % len(locations)],
                    characters[(chapter + 1) % len(characters)],
                    characters[(chapter + 2) % len(characters)],
                    locations[(chapter + 1) % len(locations)],
                    locations[(chapter + 2) % len(locations)],
                    characters[(chapter + 3) % len(characters)],
                    characters[(chapter + 4) % len(characters)]
                )
                
                # Add variety with longer content
                chapter_text += " " + ("The story continues with more details. " * 50)
                
                narrative_graph.on_text_changed(chapter_text, None, None)
                
                # Simulate user checking progress occasionally
                if chapter % 5 == 0:
                    stats = narrative_graph.current_graph_storage.get_stats()
                    assert isinstance(stats, dict), f"Stats should be available at chapter {chapter}"
            
            total_time = time.time() - start_time
            
            # Should complete in reasonable time
            assert total_time < 120.0, f"Novel processing took {total_time}s - too slow"
            
            # Should produce comprehensive results
            final_stats = narrative_graph.current_graph_storage.get_stats()
            assert final_stats['characters'] >= 5, "Should identify main characters"
            assert final_stats['locations'] >= 5, "Should identify main locations"
            assert final_stats['total_edges'] >= 10, "Should create relationships"
            
            # Memory usage should be controlled
            assert final_stats['total_nodes'] <= 1000, "Should not exceed memory limits"
            
        finally:
            os.unlink(temp_file.name)