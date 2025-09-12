#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Narrative Graph Memory Module

Advanced story tracking using NetworkX graphs and spaCy NLP.
- Character relationships and interactions
- Plot developments and continuity
- Setting details and consistency
- Narrative arcs and themes
"""

from manuskript import settings
from manuskript.ai.async_worker import async_hook
import logging
import os
import threading
from typing import Dict, Any, List, Optional

LOGGER = logging.getLogger(__name__)

# Import NetworkX conditionally
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    nx = None
    NETWORKX_AVAILABLE = False
    LOGGER.info("NetworkX not available. Using basic dictionary storage.")

# Global storage for the current project's graph
current_graph_storage = None
# Thread lock for graph operations
_graph_lock = threading.RLock()  # Reentrant lock for nested calls

def initialize():
    """
    Initialize the Narrative Graph Memory module and register hooks.
    """
    # Register hooks for various events with feature_key
    settings.register_hook("after_load", on_project_loaded, feature_key="narrativeGraphMemory", priority=5)
    settings.register_hook("before_save", on_project_save, feature_key="narrativeGraphMemory", priority=5)
    
    # Register async text processing for CPU-heavy NLP tasks
    decorated_text_processor = async_hook(cpu_heavy=True)(on_text_changed)
    settings.register_hook("text_changed", decorated_text_processor, feature_key="narrativeGraphMemory", priority=10)
    
    settings.register_hook("character_changed", on_character_changed, feature_key="narrativeGraphMemory", priority=10)
    
    LOGGER.info("Narrative Graph Memory module initialized with NetworkX support")

def on_project_loaded(project_path, main_window):
    """
    Load the narrative graph when a project is opened.
    """
    global current_graph_storage
    
    with _graph_lock:
        try:
            # Check if dependencies need to be installed
            if not NETWORKX_AVAILABLE:
                LOGGER.info("NetworkX not available. Install with: pip install networkx")
            
            # Import storage module
            from .graph_storage import load_graph
            
            # Load or create graph storage
            current_graph_storage = load_graph(project_path)
            
            stats = current_graph_storage.get_stats()
            LOGGER.info(f"Loaded narrative graph: {stats}")
            
        except Exception as e:
            LOGGER.error(f"Failed to load narrative graph: {e}")
            # Create empty storage as fallback
            from .graph_storage import GraphStorage
            current_graph_storage = GraphStorage(project_path)

def on_project_save(project_path, main_window):
    """
    Save the narrative graph when the project is saved.
    """
    global current_graph_storage
    
    with _graph_lock:
        try:
            if current_graph_storage:
                current_graph_storage.save()
                stats = current_graph_storage.get_stats()
                LOGGER.info(f"Saved narrative graph: {stats}")
            
        except Exception as e:
            LOGGER.error(f"Failed to save narrative graph: {e}")

@async_hook(cpu_heavy=True)
def on_text_changed(text: str, index, editor, **kwargs):
    """
    Analyze text changes and update the narrative graph using advanced NLP.
    This runs asynchronously to avoid blocking the UI.
    """
    global current_graph_storage
    
    # Get worker signals for progress reporting
    signals = kwargs.get('_worker_signals')
    
    # Check if graph storage is available (thread-safe check)
    with _graph_lock:
        if not current_graph_storage:
            return
    
    try:
        if signals:
            signals.status.emit("Analyzing text for narrative elements...")
            signals.progress.emit(0)
        
        # Import NLP utilities
        from .utils import extract_entities, analyze_relationships, detect_plot_points
        
        # Extract entities (characters, locations, etc.)
        if signals:
            signals.status.emit("Extracting entities...")
            signals.progress.emit(25)
        
        entities = extract_entities(text)
        
        # Thread-safe graph updates
        with _graph_lock:
            if not current_graph_storage:  # Double-check after acquiring lock
                return
                
            # Add characters to graph
            for character in entities.get('characters', []):
                current_graph_storage.add_character(character)
            
            # Add locations to graph
            for location in entities.get('locations', []):
                current_graph_storage.add_location(location)
        
        # Analyze relationships between entities
        if signals:
            signals.status.emit("Analyzing relationships...")
            signals.progress.emit(50)
        
        relationships = analyze_relationships(text, entities)
        
        with _graph_lock:
            if current_graph_storage:
                for source, rel_type, target in relationships:
                    current_graph_storage.add_relationship(source, target, rel_type)
        
        # Detect plot points
        if signals:
            signals.status.emit("Detecting plot points...")
            signals.progress.emit(75)
        
        plot_points = detect_plot_points(text)
        
        with _graph_lock:
            if current_graph_storage:
                for i, plot_point in enumerate(plot_points):
                    event_id = f"event_{plot_point['type']}_{i}_{id(text)}"  # Unique ID
                    participants = [char for char in entities.get('characters', []) 
                                  if char.lower() in plot_point['text'].lower()]
                    
                    current_graph_storage.add_event(
                        event_id, 
                        participants, 
                        plot_point['type'],
                        plot_point['text']
                    )
        
        if signals:
            signals.status.emit("Analysis complete")
            signals.progress.emit(100)
        
        LOGGER.debug(f"Processed text: {len(entities.get('characters', []))} characters, "
                    f"{len(relationships)} relationships, {len(plot_points)} plot points")
        
    except Exception as e:
        LOGGER.error(f"Failed to analyze text change: {e}")
        if signals:
            signals.status.emit(f"Analysis failed: {str(e)}")

def on_character_changed(character, index, model):
    """
    Update the narrative graph when character information changes.
    """
    global current_graph_storage
    
    with _graph_lock:
        if not current_graph_storage:
            return
        
        try:
            # Extract character name and data
            char_name = getattr(character, 'name', None)
            if not char_name:
                # Try to get name from data if it's a Character model object
                char_data = getattr(character, '_data', {})
                char_name = char_data.get(0, str(character))  # Column 0 is usually name
            
            if char_name:
                # Update character in graph with attributes
                attributes = {}
                
                # Extract character attributes if available
                if hasattr(character, '_data'):
                    # This is a Character model object
                    data = character._data
                    attributes = {
                        'description': data.get(1, ''),  # Column 1 is usually description
                        'importance': data.get(2, ''),   # Column 2 might be importance
                        'notes': data.get(3, '')         # Column 3 might be notes
                    }
                
                current_graph_storage.add_character(char_name, attributes)
                LOGGER.debug(f"Updated character '{char_name}' in narrative graph")
                
        except Exception as e:
            LOGGER.error(f"Failed to update character in narrative graph: {e}")

def get_context_for_scene(scene_id: str) -> Dict[str, Any]:
    """
    Retrieve relevant context from the narrative graph for a given scene.
    
    Args:
        scene_id: The identifier for the current scene
        
    Returns:
        dict: Context information including characters, settings, and plot points
    """
    global current_graph_storage
    
    if not current_graph_storage:
        return {}
    
    try:
        # Get graph statistics
        stats = current_graph_storage.get_stats()
        
        # Get character communities
        communities = current_graph_storage.find_communities()
        
        # Get centrality measures
        centrality = current_graph_storage.calculate_centrality()
        
        context = {
            "stats": stats,
            "character_communities": communities,
            "character_importance": centrality.get('degree', {}),
            "main_characters": list(centrality.get('degree', {}).keys())[:5] if centrality.get('degree') else []
        }
        
        return context
        
    except Exception as e:
        LOGGER.error(f"Failed to get scene context: {e}")
        return {}

def suggest_consistency_check(text: str) -> List[Dict[str, str]]:
    """
    Analyze text for potential consistency issues based on the narrative graph.
    
    Args:
        text: The text to analyze
        
    Returns:
        list: List of potential consistency issues or suggestions
    """
    global current_graph_storage
    
    if not current_graph_storage:
        return []
    
    suggestions = []
    
    try:
        from .utils import extract_entities, check_dependencies
        
        # Check if advanced NLP is available
        deps_status = check_dependencies()
        if not deps_status['model_loaded']:
            suggestions.append({
                'type': 'info',
                'message': 'Install spaCy model for advanced consistency checking: python -m spacy download en_core_web_sm'
            })
            return suggestions
        
        # Extract entities from current text
        entities = extract_entities(text)
        
        # Get existing characters from graph
        if NETWORKX_AVAILABLE and hasattr(current_graph_storage, 'graph'):
            if hasattr(current_graph_storage.graph, 'nodes'):
                existing_chars = [n for n, d in current_graph_storage.graph.nodes(data=True) 
                                if d.get('node_type') == 'character']
            else:
                existing_chars = list(current_graph_storage.graph.get('nodes', {}).keys())
        else:
            existing_chars = []
        
        # Check for new characters that might be typos
        new_chars = entities.get('characters', [])
        for char in new_chars:
            if char not in existing_chars:
                # Check for similar names (potential typos)
                similar = [c for c in existing_chars 
                          if abs(len(c) - len(char)) <= 2 and 
                          sum(1 for a, b in zip(c.lower(), char.lower()) if a != b) <= 2]
                
                if similar:
                    suggestions.append({
                        'type': 'warning',
                        'message': f"New character '{char}' is similar to existing '{similar[0]}'. Possible typo?"
                    })
        
        # Check for character relationship consistency
        # This would be expanded with more sophisticated logic
        
        return suggestions
        
    except Exception as e:
        LOGGER.error(f"Failed to check consistency: {e}")
        return [{'type': 'error', 'message': f'Consistency check failed: {str(e)}'}]