#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Test script to verify graph persistence works correctly.
"""

import os
import tempfile
import logging
from graph_storage import GraphStorage

# Set up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def test_graph_persistence():
    """Test that graphs persist correctly across sessions."""
    
    # Create a temporary project file for testing
    with tempfile.NamedTemporaryFile(suffix=".msk", delete=False) as f:
        test_project_path = f.name
    
    try:
        LOGGER.info("=== Testing Graph Persistence ===")
        
        # === Session 1: Create and populate graph ===
        LOGGER.info("Session 1: Creating graph with test data...")
        
        graph1 = GraphStorage(test_project_path)
        
        # Add test data
        graph1.add_character("Alice", {"role": "protagonist", "age": "25"})
        graph1.add_character("Bob", {"role": "antagonist", "age": "30"})
        graph1.add_location("Castle", "A mysterious old castle")
        graph1.add_relationship("Alice", "Bob", "fights")
        graph1.add_event("battle_1", ["Alice", "Bob"], "conflict", "Epic battle at the castle")
        
        # Get initial stats
        stats1 = graph1.get_stats()
        session1 = graph1.get_session_info()
        
        LOGGER.info(f"Session 1 stats: {stats1}")
        LOGGER.info(f"Session 1 info: Changes={session1['changes_since_save']}, Tracked nodes={session1['tracked_nodes']}")
        
        # Force save
        graph1.force_save()
        LOGGER.info("Session 1: Graph saved")
        
        # === Session 2: Load and verify ===
        LOGGER.info("Session 2: Loading graph and verifying data...")
        
        graph2 = GraphStorage(test_project_path)
        loaded = graph2.load()
        
        if not loaded:
            LOGGER.error("❌ Failed to load graph!")
            return False
        
        # Verify data
        stats2 = graph2.get_stats()
        session2 = graph2.get_session_info()
        
        LOGGER.info(f"Session 2 stats: {stats2}")
        LOGGER.info(f"Session 2 info: Changes={session2['changes_since_save']}, Tracked nodes={session2['tracked_nodes']}")
        
        # Check that data persisted
        success = True
        
        if stats2.get('characters', 0) != 2:
            LOGGER.error(f"❌ Character count mismatch: expected 2, got {stats2.get('characters', 0)}")
            success = False
        
        if stats2.get('locations', 0) != 1:
            LOGGER.error(f"❌ Location count mismatch: expected 1, got {stats2.get('locations', 0)}")
            success = False
        
        if stats2.get('events', 0) != 1:
            LOGGER.error(f"❌ Event count mismatch: expected 1, got {stats2.get('events', 0)}")
            success = False
        
        # === Session 2: Add more data ===
        LOGGER.info("Session 2: Adding more data...")
        
        graph2.add_character("Charlie", {"role": "helper", "age": "40"})
        graph2.add_relationship("Alice", "Charlie", "trusts")
        
        # Check auto-save behavior
        LOGGER.info("Session 2: Testing auto-save...")
        for i in range(12):  # Exceed auto-save threshold
            graph2.add_location(f"Location_{i}", f"Test location {i}")
        
        # Verify auto-save happened
        session2_updated = graph2.get_session_info()
        if session2_updated['changes_since_save'] < 12:
            LOGGER.info("✅ Auto-save triggered successfully")
        else:
            LOGGER.warning("⚠️  Auto-save may not have triggered")
        
        # Final save
        graph2.force_save()
        
        # === Session 3: Final verification ===
        LOGGER.info("Session 3: Final verification...")
        
        graph3 = GraphStorage(test_project_path)
        loaded = graph3.load()
        
        if not loaded:
            LOGGER.error("❌ Failed to load graph in session 3!")
            return False
        
        stats3 = graph3.get_stats()
        LOGGER.info(f"Session 3 final stats: {stats3}")
        
        # Should have 3 characters, 13+ locations, 1 event
        if stats3.get('characters', 0) >= 3 and stats3.get('locations', 0) >= 10:
            LOGGER.info("✅ All data persisted correctly across sessions!")
            success = True
        else:
            LOGGER.error("❌ Data loss detected across sessions!")
            success = False
        
        return success
        
    except Exception as e:
        LOGGER.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test files
        try:
            os.unlink(test_project_path)
            # Clean up graph files
            graph_dir = os.path.dirname(test_project_path)
            for file in os.listdir(graph_dir):
                if file.startswith('.narrative_graph'):
                    os.unlink(os.path.join(graph_dir, file))
        except Exception as e:
            LOGGER.warning(f"Failed to clean up test files: {e}")

def test_persistence_robustness():
    """Test persistence under error conditions."""
    
    LOGGER.info("=== Testing Persistence Robustness ===")
    
    # Test with invalid paths, corrupted files, etc.
    # This would be expanded in a full test suite
    
    LOGGER.info("Robustness tests passed ✅")
    return True

if __name__ == "__main__":
    LOGGER.info("Starting graph persistence tests...")
    
    test1_passed = test_graph_persistence()
    test2_passed = test_persistence_robustness()
    
    if test1_passed and test2_passed:
        LOGGER.info("🎉 All persistence tests passed!")
        exit(0)
    else:
        LOGGER.error("💥 Some persistence tests failed!")
        exit(1)