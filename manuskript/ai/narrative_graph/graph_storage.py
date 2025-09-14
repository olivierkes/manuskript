#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Graph Storage Module

Handles persistence and serialization of the narrative graph using NetworkX.
"""

import json
import os
import pickle
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import networkx as nx
except ImportError:
    nx = None
    logging.warning("NetworkX not installed. Graph features will be limited.")

LOGGER = logging.getLogger(__name__)

class GraphStorage:
    """
    Manages the narrative knowledge graph with NetworkX.
    Includes memory management and automatic pruning.
    """
    
    # Memory management limits
    MAX_NODES = 1000  # Maximum nodes before pruning
    MAX_EVENTS = 200  # Maximum event nodes before pruning
    PRUNE_THRESHOLD = 0.8  # Prune when 80% of limit reached
    
    def __init__(self, project_path: str):
        """
        Initialize graph storage for a project.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path
        # Use project name as basis for graph files
        base_name = os.path.splitext(project_path)[0]
        self.graph_file = base_name + ".narrative_graph.pkl"
        self.json_backup = base_name + ".narrative_graph.json"
        
        if nx:
            self.graph = nx.MultiDiGraph()
        else:
            # Fallback to dictionary if NetworkX not available
            self.graph = {
                "nodes": {},
                "edges": []
            }
        
        self.metadata = {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "last_modified": datetime.now().isoformat(),
            "stats": {},
            "last_pruned": None,
            "prune_count": 0
        }
        
        # Track node access for LRU pruning
        self.node_access_count = {}
        self.last_access_time = {}
        
        # Auto-save configuration
        self.changes_since_save = 0
        self.auto_save_threshold = 10  # Auto-save after 10 changes
        self.last_save_time = None  # Track last save time
        
        # Thread safety
        self._graph_lock = threading.RLock()
        
        # Try to load existing graph
        self.load()
    
    def _track_node_access(self, node_name: str):
        """Track node access for LRU pruning."""
        self.node_access_count[node_name] = self.node_access_count.get(node_name, 0) + 1
        self.last_access_time[node_name] = datetime.now().isoformat()
    
    def _mark_changed(self):
        """Mark that the graph has changed and check if auto-save is needed."""
        self.changes_since_save += 1
        self.metadata["last_modified"] = datetime.now().isoformat()
        
        # Auto-save if threshold reached
        if self.changes_since_save >= self.auto_save_threshold:
            try:
                self.save()
                LOGGER.debug(f"Auto-saved graph after {self.changes_since_save} changes")
            except Exception as e:
                LOGGER.error(f"Auto-save failed: {e}")
    
    def _reset_change_counter(self):
        """Reset the change counter after successful save."""
        self.changes_since_save = 0
    
    def _check_memory_limits(self):
        """Check if graph needs pruning based on memory limits."""
        if nx and isinstance(self.graph, nx.Graph):
            total_nodes = self.graph.number_of_nodes()
            event_nodes = len([n for n, d in self.graph.nodes(data=True) 
                             if d.get('node_type') == 'event'])
            
            if (total_nodes >= self.MAX_NODES * self.PRUNE_THRESHOLD or 
                event_nodes >= self.MAX_EVENTS * self.PRUNE_THRESHOLD):
                self._prune_graph()
    
    def _prune_graph(self):
        """
        Prune the graph to maintain memory limits.
        Removes least recently used event nodes first, then least connected nodes.
        """
        if not nx or not isinstance(self.graph, nx.Graph):
            return
            
        try:
            LOGGER.info("Starting graph pruning...")
            
            # First, remove old event nodes (they're most numerous and least essential)
            event_nodes = [(n, d) for n, d in self.graph.nodes(data=True) 
                          if d.get('node_type') == 'event']
            
            if len(event_nodes) > self.MAX_EVENTS * 0.7:  # Keep 70% of events
                # Sort by last access time, remove oldest
                event_nodes.sort(key=lambda x: self.last_access_time.get(x[0], ''))
                nodes_to_remove = event_nodes[:len(event_nodes) - int(self.MAX_EVENTS * 0.7)]
                
                for node_name, _ in nodes_to_remove:
                    self.graph.remove_node(node_name)
                    self.node_access_count.pop(node_name, None)
                    self.last_access_time.pop(node_name, None)
                
                LOGGER.info(f"Removed {len(nodes_to_remove)} old event nodes")
            
            # If still too many nodes, remove least connected non-character nodes
            if self.graph.number_of_nodes() > self.MAX_NODES * 0.8:
                # Get nodes that aren't characters, sorted by degree (connectivity)
                non_char_nodes = [(n, self.graph.degree(n)) for n, d in self.graph.nodes(data=True) 
                                if d.get('node_type') != 'character']
                non_char_nodes.sort(key=lambda x: x[1])  # Sort by degree (ascending)
                
                if non_char_nodes:
                    nodes_to_remove = non_char_nodes[:len(non_char_nodes) // 4]  # Remove 25%
                    
                    for node_name, _ in nodes_to_remove:
                        self.graph.remove_node(node_name)
                        self.node_access_count.pop(node_name, None)
                        self.last_access_time.pop(node_name, None)
                    
                    LOGGER.info(f"Removed {len(nodes_to_remove)} low-connectivity nodes")
                
                # If STILL too many nodes and we're way over limit, remove least accessed characters
                if self.graph.number_of_nodes() >= self.MAX_NODES:
                    # Sort characters by access count
                    char_nodes = [(n, self.node_access_count.get(n, 0)) 
                                 for n, d in self.graph.nodes(data=True) 
                                 if d.get('node_type') == 'character']
                    char_nodes.sort(key=lambda x: x[1])  # Sort by access count (ascending)
                    
                    # Calculate how many to remove to get well under limit
                    target = int(self.MAX_NODES * 0.7)  # Target 70% capacity
                    excess = self.graph.number_of_nodes() - target
                    nodes_to_remove = char_nodes[:min(excess, len(char_nodes) // 3)]  # Remove up to 1/3 of characters
                    
                    for node_name, _ in nodes_to_remove:
                        self.graph.remove_node(node_name)
                        self.node_access_count.pop(node_name, None)
                        self.last_access_time.pop(node_name, None)
                    
                    LOGGER.info(f"Removed {len(nodes_to_remove)} least accessed characters")
            
            # Update metadata
            self.metadata["last_pruned"] = datetime.now().isoformat()
            self.metadata["prune_count"] = self.metadata.get("prune_count", 0) + 1
            
            LOGGER.info(f"Graph pruning complete. Nodes: {self.graph.number_of_nodes()}")
            
        except Exception as e:
            LOGGER.error(f"Error during graph pruning: {e}")
    
    def add_character(self, name: str, attributes: Dict[str, Any] = None):
        """
        Add a character node to the graph.
        
        Args:
            name: Character name
            attributes: Character attributes (traits, descriptions, etc.)
        """
        with self._graph_lock:
            self._track_node_access(name)
            
            if nx and hasattr(self.graph, 'nodes'):
                # NetworkX graph available and initialized
                if self.graph.has_node(name):
                    # Update existing node attributes
                    existing_attrs = self.graph.nodes[name].get('attributes', {})
                    existing_attrs.update(attributes or {})
                    self.graph.nodes[name]['attributes'] = existing_attrs
                else:
                    self.graph.add_node(
                        name,
                        node_type="character",
                        attributes=attributes or {},
                        first_seen=datetime.now().isoformat()
                    )
                LOGGER.debug(f"Added/updated character node: {name}")
            else:
                # Fallback to dict-based storage
                if not isinstance(self.graph, dict):
                    self.graph = {"nodes": {}, "edges": []}
                if "nodes" not in self.graph:
                    self.graph["nodes"] = {}
                self.graph["nodes"][name] = {
                    "node_type": "character",
                    "attributes": attributes or {}
                }
            
            # Mark as changed and check if pruning is needed
            self._mark_changed()
            self._check_memory_limits()
    
    def add_location(self, name: str, description: str = ""):
        """
        Add a location node to the graph.
        
        Args:
            name: Location name
            description: Location description
        """
        with self._graph_lock:
            self._track_node_access(name)
            
            if nx and hasattr(self.graph, 'nodes'):
                if self.graph.has_node(name):
                    # Update existing node if it's a location
                    if self.graph.nodes[name].get('node_type') == 'location':
                        existing_desc = self.graph.nodes[name].get('description', '')
                        if description and not existing_desc:
                            self.graph.nodes[name]['description'] = description
                else:
                    self.graph.add_node(
                        name,
                        node_type="location",
                        description=description,
                        first_seen=datetime.now().isoformat()
                    )
                    LOGGER.debug(f"Added location node: {name}")
            else:
                # Fallback to dict-based storage
                if not isinstance(self.graph, dict):
                    self.graph = {"nodes": {}, "edges": []}
                if "nodes" not in self.graph:
                    self.graph["nodes"] = {}
                self.graph["nodes"][name] = {
                    "node_type": "location",
                    "description": description
                }
            
            # Mark as changed and check if pruning is needed
            self._mark_changed()
            self._check_memory_limits()
    
    def add_relationship(self, source: str, target: str, 
                        rel_type: str, attributes: Dict[str, Any] = None):
        """
        Add a relationship edge between nodes.
        
        Args:
            source: Source node name
            target: Target node name
            rel_type: Type of relationship (e.g., "knows", "loves", "visited")
            attributes: Additional relationship attributes
        """
        with self._graph_lock:
            if nx and hasattr(self.graph, 'nodes'):
                self.graph.add_edge(
                    source,
                    target,
                    relationship=rel_type,
                    timestamp=datetime.now().isoformat(),
                    **(attributes or {})
                )
                LOGGER.debug(f"Added relationship: {source} --[{rel_type}]--> {target}")
            else:
                # Fallback to dict-based storage
                if not isinstance(self.graph, dict):
                    self.graph = {"nodes": {}, "edges": []}
                if "edges" not in self.graph:
                    self.graph["edges"] = []
                self.graph["edges"].append({
                    "source": source,
                    "target": target,
                    "type": rel_type,
                    "attributes": attributes or {}
                })
    
    def add_event(self, event_id: str, participants: list, 
                  event_type: str, description: str = ""):
        """
        Add an event node with connections to participants.
        
        Args:
            event_id: Unique event identifier
            participants: List of character names involved
            event_type: Type of event
            description: Event description
        """
        with self._graph_lock:
            if nx and hasattr(self.graph, 'nodes'):
                # Add event node
                self.graph.add_node(
                    event_id,
                    node_type="event",
                    event_type=event_type,
                    description=description,
                    timestamp=datetime.now().isoformat()
                )
                
                # Connect participants to event
                for participant in participants:
                    self.graph.add_edge(
                        participant,
                        event_id,
                        relationship="participated_in"
                    )
                
                LOGGER.debug(f"Added event: {event_id} with {len(participants)} participants")
    
    def get_character_connections(self, character: str, depth: int = 1):
        """
        Get all connections for a character up to specified depth.
        
        Args:
            character: Character name
            depth: How many hops to explore
            
        Returns:
            Dict of connected nodes and relationships
        """
        if nx and self.graph and character in self.graph:
            # Use NetworkX to find neighbors
            connections = {}
            
            if depth == 1:
                connections = dict(self.graph[character])
            else:
                # BFS to specified depth
                subgraph = nx.ego_graph(self.graph, character, radius=depth)
                connections = {
                    "nodes": list(subgraph.nodes(data=True)),
                    "edges": list(subgraph.edges(data=True))
                }
            
            return connections
        
        return {}
    
    def find_communities(self):
        """
        Detect character communities/groups in the story.
        
        Returns:
            List of character groups
        """
        if nx and hasattr(self.graph, 'nodes'):
            # Filter to only character nodes
            char_nodes = [n for n, d in self.graph.nodes(data=True) 
                         if d.get('node_type') == 'character']
            
            if len(char_nodes) > 1:
                char_subgraph = self.graph.subgraph(char_nodes)
                
                # Convert to undirected for community detection
                if char_subgraph.number_of_edges() > 0:
                    undirected = char_subgraph.to_undirected()
                    communities = list(nx.community.greedy_modularity_communities(undirected))
                    
                    return [list(community) for community in communities]
        
        return []
    
    def calculate_centrality(self):
        """
        Calculate character importance/centrality in the narrative.
        
        Returns:
            Dict of character centrality scores
        """
        if nx and hasattr(self.graph, 'nodes'):
            # Filter character nodes
            char_nodes = [n for n, d in self.graph.nodes(data=True) 
                         if d.get('node_type') == 'character']
            
            if char_nodes:
                char_subgraph = self.graph.subgraph(char_nodes)
                
                if char_subgraph.number_of_edges() > 0:
                    # Calculate different centrality measures
                    centrality = {
                        "degree": nx.degree_centrality(char_subgraph),
                        "betweenness": nx.betweenness_centrality(char_subgraph),
                        "closeness": nx.closeness_centrality(char_subgraph)
                    }
                    
                    return centrality
        
        return {}
    
    def save(self):
        """
        Save the graph to disk with full metadata.
        """
        self.metadata["last_modified"] = datetime.now().isoformat()
        
        try:
            if nx and isinstance(self.graph, nx.Graph):
                # Save as pickle for full graph preservation including access tracking
                save_data = {
                    'graph': self.graph,
                    'metadata': self.metadata,
                    'node_access_count': self.node_access_count,
                    'last_access_time': self.last_access_time
                }
                
                with open(self.graph_file, 'wb') as f:
                    pickle.dump(save_data, f)
                
                # Also save JSON backup for portability (without access data)
                self.save_json_backup()
                
                LOGGER.info(f"Saved narrative graph to {self.graph_file} (nodes: {self.graph.number_of_nodes()}, edges: {self.graph.number_of_edges()})")
            else:
                # Fallback to JSON only
                self.save_json_backup()
                LOGGER.info(f"Saved narrative graph (fallback mode) to {self.json_backup}")
                
        except Exception as e:
            LOGGER.error(f"Failed to save graph: {e}")
            # Try JSON as emergency fallback
            try:
                self.save_json_backup()
                LOGGER.info("Emergency save to JSON succeeded")
            except Exception as e2:
                LOGGER.error(f"Emergency JSON save also failed: {e2}")
        
        # Reset change counter and update last save time on successful save
        self._reset_change_counter()
        self.last_save_time = datetime.now().isoformat()
    
    def save_json_backup(self):
        """
        Save a JSON representation of the graph.
        """
        try:
            if nx and isinstance(self.graph, nx.Graph):
                # Convert NetworkX graph to JSON-serializable format
                data = {
                    'nodes': [
                        {'id': n, **d} 
                        for n, d in self.graph.nodes(data=True)
                    ],
                    'edges': [
                        {'source': u, 'target': v, **d}
                        for u, v, d in self.graph.edges(data=True)
                    ],
                    'metadata': self.metadata
                }
            else:
                data = {
                    'graph': self.graph,
                    'metadata': self.metadata
                }
            
            with open(self.json_backup, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            LOGGER.debug(f"Saved JSON backup to {self.json_backup}")
            
        except Exception as e:
            LOGGER.error(f"Failed to save JSON backup: {e}")
    
    def load(self):
        """
        Load the graph from disk with full metadata and access tracking.
        
        Returns:
            bool: True if successful
        """
        try:
            # Try pickle first (preferred format with full data)
            if os.path.exists(self.graph_file):
                with open(self.graph_file, 'rb') as f:
                    data = pickle.load(f)
                    
                self.graph = data['graph']
                self.metadata = data.get('metadata', self.metadata)
                
                # Restore access tracking data if available
                self.node_access_count = data.get('node_access_count', {})
                self.last_access_time = data.get('last_access_time', {})
                
                # Reset change counter for fresh session
                self.changes_since_save = 0
                
                stats = self.get_stats()
                LOGGER.info(f"Loaded narrative graph from pickle: {stats}")
                
                # Validate graph integrity
                if self._validate_graph():
                    return True
                else:
                    LOGGER.warning("Graph failed validation, starting fresh")
                    return False
            
            # Fall back to JSON
            elif os.path.exists(self.json_backup):
                return self.load_from_json()
            
        except Exception as e:
            LOGGER.error(f"Failed to load graph from pickle: {e}")
            # Try JSON as fallback
            return self.load_from_json()
        
        # No existing graph found
        LOGGER.info("No existing narrative graph found, starting fresh")
        return False
    
    def load_from_json(self):
        """
        Load graph from JSON backup.
        
        Returns:
            bool: True if successful
        """
        try:
            with open(self.json_backup, 'r') as f:
                data = json.load(f)
            
            if nx:
                # Reconstruct NetworkX graph
                self.graph = nx.MultiDiGraph()
                
                if 'nodes' in data:
                    for node in data['nodes']:
                        node_id = node.pop('id')
                        self.graph.add_node(node_id, **node)
                
                if 'edges' in data:
                    for edge in data['edges']:
                        source = edge.pop('source')
                        target = edge.pop('target')
                        self.graph.add_edge(source, target, **edge)
            else:
                # Use dictionary fallback
                self.graph = data.get('graph', {"nodes": {}, "edges": []})
            
            self.metadata = data.get('metadata', self.metadata)
            
            # Reset change counter and access tracking for fresh session
            self.changes_since_save = 0
            self.node_access_count = {}
            self.last_access_time = {}
            
            LOGGER.info(f"Loaded narrative graph from JSON: {self.json_backup}")
            
            # Validate graph integrity
            if self._validate_graph():
                return True
            else:
                LOGGER.warning("Graph loaded from JSON failed validation")
                return False
            
        except Exception as e:
            LOGGER.error(f"Failed to load JSON backup: {e}")
            return False
    
    def get_stats(self):
        """
        Get graph statistics.
        
        Returns:
            Dict of graph statistics
        """
        stats = {}
        
        if nx and isinstance(self.graph, nx.Graph):
            stats = {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "characters": len([n for n, d in self.graph.nodes(data=True) 
                                 if d.get('node_type') == 'character']),
                "locations": len([n for n, d in self.graph.nodes(data=True) 
                                if d.get('node_type') == 'location']),
                "events": len([n for n, d in self.graph.nodes(data=True) 
                             if d.get('node_type') == 'event']),
                "density": nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0
            }
        else:
            # Dictionary fallback
            if isinstance(self.graph, dict):
                nodes = self.graph.get("nodes", {})
                stats = {
                    "total_nodes": len(nodes),
                    "total_edges": len(self.graph.get("edges", [])),
                    "characters": len([n for n, data in nodes.items() 
                                     if data.get('node_type') == 'character']),
                    "locations": len([n for n, data in nodes.items() 
                                    if data.get('node_type') == 'location']),
                    "events": len([n for n, data in nodes.items() 
                                 if data.get('node_type') == 'event']),
                    "density": 0  # Can't easily calculate for dict
                }
        
        self.metadata["stats"] = stats
        return stats
    
    def _validate_graph(self):
        """
        Validate the loaded graph for integrity.
        
        Returns:
            bool: True if graph is valid
        """
        try:
            if nx and isinstance(self.graph, nx.Graph):
                # Check for basic graph integrity
                node_count = self.graph.number_of_nodes()
                edge_count = self.graph.number_of_edges()
                
                if node_count < 0 or edge_count < 0:
                    return False
                
                # Check for isolated issues
                for node in self.graph.nodes():
                    if not isinstance(node, str) or len(node) == 0:
                        LOGGER.warning(f"Invalid node found: {repr(node)}")
                        return False
                
                # Basic consistency check passed
                LOGGER.debug(f"Graph validation passed: {node_count} nodes, {edge_count} edges")
                return True
            
            elif isinstance(self.graph, dict):
                # Validate dictionary format
                if "nodes" not in self.graph or "edges" not in self.graph:
                    return False
                
                nodes = self.graph.get("nodes", {})
                edges = self.graph.get("edges", [])
                
                if not isinstance(nodes, dict) or not isinstance(edges, list):
                    return False
                
                return True
            
            return False
            
        except Exception as e:
            LOGGER.error(f"Graph validation failed: {e}")
            return False
    
    def get_session_info(self):
        """
        Get information about the current session state.
        
        Returns:
            dict: Session information
        """
        return {
            "changes_since_save": self.changes_since_save,
            "auto_save_threshold": self.auto_save_threshold,
            "tracked_nodes": len(self.node_access_count),
            "last_access_entries": len(self.last_access_time),
            "last_save_time": self.last_save_time,
            "metadata": self.metadata,
            "graph_files": {
                "pickle_exists": os.path.exists(self.graph_file),
                "json_exists": os.path.exists(self.json_backup),
                "pickle_size": os.path.getsize(self.graph_file) if os.path.exists(self.graph_file) else 0,
                "json_size": os.path.getsize(self.json_backup) if os.path.exists(self.json_backup) else 0
            }
        }
    
    def force_save(self):
        """
        Force an immediate save regardless of change threshold.
        """
        old_threshold = self.auto_save_threshold
        self.auto_save_threshold = 0  # Force save
        try:
            self.save()
            LOGGER.info("Force save completed")
        finally:
            self.auto_save_threshold = old_threshold

# Convenience functions
def save_graph(storage: GraphStorage):
    """Save the narrative graph."""
    storage.save()

def load_graph(project_path: str) -> GraphStorage:
    """Load or create a narrative graph for a project."""
    storage = GraphStorage(project_path)
    storage.load()
    return storage