#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Narrative Graph Memory Module

This module provides contextual memory for your story by tracking:
- Character relationships and interactions
- Plot developments
- Setting details
- Narrative arcs
"""

from manuskript import settings
import logging
import json
import os

LOGGER = logging.getLogger(__name__)

# Store the narrative graph in memory
narrative_graph = {
    "characters": {},
    "relationships": [],
    "plot_points": [],
    "settings": {},
    "themes": []
}

def initialize():
    """
    Initialize the Narrative Graph Memory module and register hooks.
    """
    # Register hooks for various events with feature_key
    settings.register_hook("after_load", on_project_loaded, feature_key="narrativeGraphMemory", priority=5)
    settings.register_hook("before_save", on_project_save, feature_key="narrativeGraphMemory", priority=5)
    settings.register_hook("text_changed", on_text_changed, feature_key="narrativeGraphMemory", priority=10)
    settings.register_hook("character_changed", on_character_changed, feature_key="narrativeGraphMemory", priority=10)
    
    LOGGER.info("Narrative Graph Memory module initialized")

def on_project_loaded(project_path, main_window):
    """
    Load the narrative graph when a project is opened.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        # Try to load existing narrative graph
        graph_file = os.path.join(os.path.dirname(project_path), ".narrative_graph.json")
        if os.path.exists(graph_file):
            with open(graph_file, 'r') as f:
                global narrative_graph
                narrative_graph = json.load(f)
                LOGGER.info(f"Loaded narrative graph from {graph_file}")
    except Exception as e:
        LOGGER.error(f"Failed to load narrative graph: {e}")

def on_project_save(project_path, main_window):
    """
    Save the narrative graph when the project is saved.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        # Save narrative graph alongside project
        graph_file = os.path.join(os.path.dirname(project_path), ".narrative_graph.json")
        with open(graph_file, 'w') as f:
            json.dump(narrative_graph, f, indent=2)
            LOGGER.debug(f"Saved narrative graph to {graph_file}")
    except Exception as e:
        LOGGER.error(f"Failed to save narrative graph: {e}")

def on_text_changed(text, index, editor):
    """
    Analyze text changes and update the narrative graph.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        # This is where you would implement the actual AI analysis
        # For now, just log the change
        LOGGER.debug(f"Text changed, analyzing for narrative elements...")
        
        # Example: Extract character mentions (simplified)
        # In a real implementation, this would use NLP/AI
        words = text.split()
        for word in words:
            # Simple heuristic: capitalized words might be character names
            if word and word[0].isupper() and len(word) > 2:
                if word not in narrative_graph["characters"]:
                    narrative_graph["characters"][word] = {
                        "mentions": 0,
                        "contexts": []
                    }
                narrative_graph["characters"][word]["mentions"] += 1
                
    except Exception as e:
        LOGGER.error(f"Failed to analyze text change: {e}")

def on_character_changed(character, index, model):
    """
    Update the narrative graph when character information changes.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        # Update character information in the graph
        char_name = getattr(character, 'name', str(character))
        if char_name:
            if char_name not in narrative_graph["characters"]:
                narrative_graph["characters"][char_name] = {}
            
            # Store character metadata
            narrative_graph["characters"][char_name]["last_updated"] = True
            LOGGER.debug(f"Updated character '{char_name}' in narrative graph")
            
    except Exception as e:
        LOGGER.error(f"Failed to update character in narrative graph: {e}")

def get_context_for_scene(scene_id):
    """
    Retrieve relevant context from the narrative graph for a given scene.
    
    Args:
        scene_id: The identifier for the current scene
        
    Returns:
        dict: Context information including characters, settings, and plot points
    """
    if not settings.aiFeatures.get("narrativeGraphMemory", False):
        return {}
    
    # This would be implemented with actual AI logic to provide
    # relevant context based on the narrative graph
    context = {
        "characters": list(narrative_graph["characters"].keys()),
        "recent_plot_points": narrative_graph["plot_points"][-5:] if narrative_graph["plot_points"] else [],
        "active_themes": narrative_graph["themes"]
    }
    
    return context

def suggest_consistency_check(text):
    """
    Analyze text for potential consistency issues based on the narrative graph.
    
    Args:
        text: The text to analyze
        
    Returns:
        list: List of potential consistency issues or suggestions
    """
    if not settings.aiFeatures.get("narrativeGraphMemory", False):
        return []
    
    suggestions = []
    
    # This would use AI to check for consistency issues
    # For example: character behavior, timeline issues, setting details
    
    return suggestions