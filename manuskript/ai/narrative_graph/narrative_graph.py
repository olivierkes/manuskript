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
from manuskript.enums import Outline
from manuskript.ai.async_worker import async_hook
import logging
import os
import threading
from typing import Dict, Any, List, Optional

LOGGER = logging.getLogger(__name__)

# Import the new high-performance graph engine
try:
    from .graph_engine import NarrativeGraphEngine, EntityType, RelationType
    ENGINE_AVAILABLE = True
except ImportError:
    ENGINE_AVAILABLE = False
    LOGGER.warning("NarrativeGraphEngine not available, falling back to NetworkX")
    # Import NetworkX conditionally as fallback
    try:
        import networkx as nx
        NETWORKX_AVAILABLE = True
    except ImportError:
        nx = None
        NETWORKX_AVAILABLE = False
        LOGGER.info("NetworkX not available. Using basic dictionary storage.")

# Global storage for the current project's graph
current_graph_storage = None
current_graph_engine = None  # New high-performance engine
# Thread lock for graph operations
_graph_lock = threading.RLock()  # Reentrant lock for nested calls

def initialize(project_path=None):
    """
    Initialize the Narrative Graph Memory module and register hooks.
    
    Args:
        project_path: Optional project path for direct initialization (used in testing)
    """
    global current_graph_storage
    
    # If project_path provided, initialize directly (for testing)
    if project_path:
        from .graph_storage import GraphStorage
        current_graph_storage = GraphStorage(project_path)
        LOGGER.info(f"Narrative Graph initialized directly with project: {project_path}")
    
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
    Load the narrative graph when a project is opened and scan existing content.
    """
    global current_graph_storage, current_graph_engine
    
    LOGGER.info(f"on_project_loaded called with project_path: {project_path}")
    
    with _graph_lock:
        try:
            # Try to use new engine first
            if ENGINE_AVAILABLE:
                current_graph_engine = NarrativeGraphEngine(project_path)
                # Try to load existing data
                if current_graph_engine.load():
                    stats = current_graph_engine.get_statistics()
                    LOGGER.info(f"Loaded narrative graph engine: {stats}")
                else:
                    LOGGER.info("No existing graph data, will scan content")
                
                # If graph is empty, scan existing project content
                if len(current_graph_engine.entities) == 0:
                    LOGGER.info("Empty graph detected, scanning existing content...")
                    _scan_project_content(main_window)
            else:
                # Fall back to old storage
                # Check if dependencies need to be installed
                if not NETWORKX_AVAILABLE:
                    LOGGER.info("NetworkX not available. Install with: pip install networkx")
                
                # Import storage module
                from .graph_storage import load_graph
                
                # Load or create graph storage
                current_graph_storage = load_graph(project_path)
                
                stats = current_graph_storage.get_stats()
                LOGGER.info(f"Loaded narrative graph: {stats}")
                
                # If graph is empty, scan existing project content
                if current_graph_storage.graph.number_of_nodes() == 0:
                    LOGGER.info("Empty graph detected, scanning existing content...")
                    _scan_project_content(main_window)
            
        except Exception as e:
            LOGGER.error(f"Failed to load narrative graph: {e}")
            # Create empty engine/storage as fallback
            if ENGINE_AVAILABLE:
                current_graph_engine = NarrativeGraphEngine(project_path)
            else:
                from .graph_storage import GraphStorage
                current_graph_storage = GraphStorage(project_path)
            # Try to scan content even with new storage
            try:
                _scan_project_content(main_window)
            except Exception as scan_error:
                LOGGER.error(f"Failed to scan project content: {scan_error}")

def _scan_project_content(main_window):
    """
    Scan all existing content in the project using smart extraction.
    """
    global current_graph_storage, current_graph_engine
    
    LOGGER.info("Starting smart project content scan...")
    
    if not current_graph_storage and not current_graph_engine:
        LOGGER.warning("No graph storage/engine available for content scan")
        return
    
    try:
        # Try to use smart extraction first
        try:
            from .smart_extraction import SmartEntityExtractor
            use_smart = True
            extractor = SmartEntityExtractor(main_window)
            LOGGER.info("Using smart entity extraction")
        except ImportError:
            LOGGER.info("Smart extraction not available, falling back to basic extraction")
            use_smart = False
            from .utils import extract_entities, analyze_relationships
        
        # Clear existing graph data first
        if current_graph_engine:
            current_graph_engine.clear()
        elif current_graph_storage:
            current_graph_storage.clear()
        
        if use_smart:
            # First, add all existing characters and locations from models
            existing_chars = extractor.get_existing_characters()
            existing_locs = extractor.get_existing_locations()
            
            # Add existing entities to graph
            for char_id, char_data in existing_chars.items():
                if current_graph_engine:
                    current_graph_engine.add_entity(
                        char_data['name'],
                        EntityType.CHARACTER,
                        motivation=char_data.get('motivation', '')
                    )
                elif current_graph_storage:
                    current_graph_storage.add_character(
                        char_data['name'],
                        description=char_data.get('motivation', '')
                    )
                LOGGER.debug(f"Added existing character: {char_data['name']}")
            
            for loc_id, loc_data in existing_locs.items():
                if current_graph_engine:
                    current_graph_engine.add_entity(
                        loc_data['name'],
                        EntityType.LOCATION,
                        description=loc_data.get('description', '')
                    )
                elif current_graph_storage:
                    current_graph_storage.add_location(
                        loc_data['name'],
                        description=loc_data.get('description', '')
                    )
                LOGGER.debug(f"Added existing location: {loc_data['name']}")
        
        # Get the outline model from main window
        if hasattr(main_window, 'mdlOutline') and main_window.mdlOutline:
            from manuskript.enums import Outline
            
            items_processed = 0
            entities_found = 0
            relationships_found = 0
            
            # Recursively scan all text items in the outline
            def scan_item(item):
                nonlocal items_processed, entities_found, relationships_found
                
                # Get text content
                text = item.data(Outline.text.value)
                title = item.data(Outline.title.value) or ""
                item_id = item.data(Outline.ID.value) or ""
                
                if text:
                    items_processed += 1
                    try:
                        if use_smart:
                            # Use smart extraction
                            entities = extractor.extract_from_text(text)
                            
                            # Add new characters not in existing models
                            for character in entities.get("characters", []):
                                if character not in [c['name'] for c in existing_chars.values()]:
                                    if current_graph_engine:
                                        current_graph_engine.add_entity(character, EntityType.CHARACTER)
                                    elif current_graph_storage:
                                        current_graph_storage.add_character(character)
                                    entities_found += 1
                                    LOGGER.debug(f"Found new character: {character}")
                            
                            # Add new locations not in existing models
                            for location in entities.get("locations", []):
                                if location not in [l['name'] for l in existing_locs.values()]:
                                    if current_graph_engine:
                                        current_graph_engine.add_entity(location, EntityType.LOCATION)
                                    elif current_graph_storage:
                                        current_graph_storage.add_location(location)
                                    entities_found += 1
                                    LOGGER.debug(f"Found new location: {location}")
                            
                            # Analyze character interactions
                            interactions = extractor.analyze_character_interactions(
                                text,
                                entities.get('characters', [])
                            )
                            
                            for interaction in interactions:
                                if current_graph_engine:
                                    # Map interaction type to RelationType
                                    rel_type = RelationType.INTERACTS  # Default
                                    interaction_type = interaction['type'].lower()
                                    if 'love' in interaction_type:
                                        rel_type = RelationType.LOVES
                                    elif 'hate' in interaction_type:
                                        rel_type = RelationType.ENEMY
                                    elif 'friend' in interaction_type or 'help' in interaction_type:
                                        rel_type = RelationType.FRIEND
                                    elif 'know' in interaction_type or 'met' in interaction_type:
                                        rel_type = RelationType.KNOWS
                                    
                                    # Get entity IDs
                                    char1_id = f"character_{interaction['character1'].lower().replace(' ', '_')}"
                                    char2_id = f"character_{interaction['character2'].lower().replace(' ', '_')}"
                                    current_graph_engine.add_relationship(char1_id, char2_id, rel_type)
                                elif current_graph_storage:
                                    current_graph_storage.add_relationship(
                                        interaction['character1'],
                                        interaction['character2'],
                                        interaction['type']
                                    )
                                relationships_found += 1
                                LOGGER.debug(f"Found interaction: {interaction['character1']} -> {interaction['character2']} ({interaction['type']})")
                        else:
                            # Fall back to basic extraction
                            entities = extract_entities(text)
                            
                            # Add to graph
                            for character in entities.get("characters", []):
                                current_graph_storage.add_character(character)
                                entities_found += 1
                                LOGGER.debug(f"Found character: {character}")
                            for location in entities.get("locations", []):
                                current_graph_storage.add_location(location)
                                entities_found += 1
                                LOGGER.debug(f"Found location: {location}")
                            
                            # Extract and add relationships
                            relationships = analyze_relationships(text, entities)
                            for source, rel_type, target in relationships:
                                current_graph_storage.add_relationship(
                                    source, target, rel_type
                                )
                                relationships_found += 1
                                LOGGER.debug(f"Found relationship: {source} -> {target} ({rel_type})")
                            
                    except Exception as e:
                        LOGGER.debug(f"Failed to process item text: {e}")
                
                # Recursively process children
                for i in range(item.childCount()):
                    scan_item(item.child(i))
            
            # Start scanning from root
            root = main_window.mdlOutline.rootItem
            scan_item(root)
            
            if current_graph_engine:
                stats = current_graph_engine.get_statistics()
            elif current_graph_storage:
                stats = current_graph_storage.get_stats()
            else:
                stats = {}
            LOGGER.info(f"Content scan complete. Processed {items_processed} items, found {entities_found} new entities, {relationships_found} relationships. Graph stats: {stats}")
            
    except Exception as e:
        LOGGER.error(f"Failed to scan project content: {e}", exc_info=True)

def on_project_save(project_path, main_window):
    """
    Save the narrative graph when the project is saved.
    """
    global current_graph_storage, current_graph_engine
    
    with _graph_lock:
        try:
            if current_graph_engine:
                current_graph_engine.save()
                stats = current_graph_engine.get_statistics()
                LOGGER.info(f"Saved narrative graph engine: {stats}")
            elif current_graph_storage:
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
        
        # Check for numeric inconsistencies (ages, numbers, etc.)
        import re
        
        # Find all numbers associated with characters
        char_numbers = {}
        for char in new_chars:
            # Find numbers near character mentions
            pattern = rf"{char}.*?(\d+)|(\d+).*?{char}"
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                num = match[0] if match[0] else match[1]
                if num:
                    if char not in char_numbers:
                        char_numbers[char] = []
                    char_numbers[char].append(int(num))
        
        # Check for inconsistent numbers for the same character
        for char, numbers in char_numbers.items():
            if len(numbers) > 1 and len(set(numbers)) > 1:
                # Check if numbers could be ages (reasonable range)
                if all(10 <= n <= 100 for n in numbers):
                    suggestions.append({
                        'type': 'warning',
                        'message': f"Character '{char}' has inconsistent ages: {sorted(set(numbers))}. Please verify timeline consistency."
                    })
                else:
                    suggestions.append({
                        'type': 'info',
                        'message': f"Character '{char}' is associated with different numbers: {sorted(set(numbers))}. Verify if this is intentional."
                    })
        
        # Check for timeline inconsistencies
        age_pattern = r"(\d+)[\s-]*year[s]?[\s-]*old"
        ages_mentioned = re.findall(age_pattern, text, re.IGNORECASE)
        if len(set(ages_mentioned)) > 2:  # Multiple different ages mentioned
            suggestions.append({
                'type': 'info',
                'message': f"Multiple ages mentioned ({', '.join(set(ages_mentioned))} years). Ensure timeline consistency."
            })
        
        # Check for duplicate phrases or repetitive content
        sentences = text.split('.')
        if len(sentences) > 1:
            # Look for very similar sentences
            for i, sent1 in enumerate(sentences[:-1]):
                for sent2 in sentences[i+1:]:
                    if len(sent1) > 10 and len(sent2) > 10:
                        # Simple similarity check
                        words1 = set(sent1.lower().split())
                        words2 = set(sent2.lower().split())
                        if words1 and words2:
                            overlap = len(words1 & words2) / min(len(words1), len(words2))
                            if overlap > 0.8:
                                suggestions.append({
                                    'type': 'info',
                                    'message': 'Detected potentially repetitive content. Consider varying your descriptions.'
                                })
                                break
        
        return suggestions
        
    except Exception as e:
        LOGGER.error(f"Failed to check consistency: {e}")
        return [{'type': 'error', 'message': f'Consistency check failed: {str(e)}'}]