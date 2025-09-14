#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
High-Performance Graph Engine for Narrative Analysis
Optimized for speed, memory efficiency, and thread safety.
"""

import logging
import threading
import time
import weakref
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
import json
import weakref
from enum import Enum, auto

LOGGER = logging.getLogger(__name__)

class EntityType(Enum):
    """Entity types in the narrative."""
    CHARACTER = auto()
    LOCATION = auto()
    OBJECT = auto()
    EVENT = auto()
    THEME = auto()
    CONCEPT = auto()

class RelationType(Enum):
    """Relationship types between entities."""
    # Character relationships
    KNOWS = auto()
    LOVES = auto()
    HATES = auto()
    FAMILY = auto()
    FRIEND = auto()
    ENEMY = auto()
    WORKS_WITH = auto()
    INTERACTS = auto()  # General interaction
    
    # Action relationships
    TALKS_TO = auto()
    FIGHTS = auto()
    HELPS = auto()
    BETRAYS = auto()
    SAVES = auto()
    
    # Location relationships
    LOCATED_AT = auto()
    TRAVELS_TO = auto()
    LIVES_IN = auto()
    VISITS = auto()
    
    # Event relationships
    PARTICIPATES_IN = auto()
    CAUSES = auto()
    AFFECTED_BY = auto()

@dataclass
class Entity:
    """Represents an entity in the narrative."""
    id: str
    name: str
    type: EntityType
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_appearance: Optional[str] = None
    last_appearance: Optional[str] = None
    mention_count: int = 0
    importance_score: float = 0.0
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.id == other.id
        return False

@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_id: str
    target_id: str
    type: RelationType
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    occurrences: List[str] = field(default_factory=list)  # Scene IDs where this relationship appears
    
    def __hash__(self):
        return hash((self.source_id, self.target_id, self.type))

class GraphIndex:
    """High-performance index for graph queries."""
    
    def __init__(self):
        # Entity indexes
        self.entities_by_type: Dict[EntityType, Set[str]] = defaultdict(set)
        self.entities_by_name: Dict[str, Set[str]] = defaultdict(set)
        self.entities_by_scene: Dict[str, Set[str]] = defaultdict(set)
        
        # Relationship indexes
        self.relationships_by_type: Dict[RelationType, Set[Tuple[str, str]]] = defaultdict(set)
        self.outgoing_edges: Dict[str, Set[str]] = defaultdict(set)
        self.incoming_edges: Dict[str, Set[str]] = defaultdict(set)
        
        # Statistics cache with TTL
        self._stats_cache = {}
        self._cache_timestamps = {}
        self._cache_dirty = True
        self._cache_ttl = 300  # 5 minutes TTL
        self._max_cache_size = 50  # Maximum cache entries
    
    def invalidate_cache(self):
        """Mark cache as dirty."""
        self._cache_dirty = True
    
    def _cleanup_expired_cache(self):
        """Remove expired cache entries based on TTL."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > self._cache_ttl
        ]
        
        for key in expired_keys:
            self._stats_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
    
    def _ensure_cache_size_limit(self):
        """Ensure cache doesn't exceed maximum size limit."""
        if len(self._stats_cache) <= self._max_cache_size:
            return
            
        # Remove oldest entries (LRU eviction)
        items = sorted(self._cache_timestamps.items(), key=lambda x: x[1])
        to_remove = len(items) - self._max_cache_size
        
        for i in range(to_remove):
            key = items[i][0]
            self._stats_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
    
    def _get_cache_entry(self, key: str):
        """Get cache entry if valid, None if expired or missing."""
        self._cleanup_expired_cache()
        
        if key in self._stats_cache and not self._cache_dirty:
            # Update timestamp (LRU)
            self._cache_timestamps[key] = time.time()
            return self._stats_cache[key]
        return None
    
    def _set_cache_entry(self, key: str, value):
        """Set cache entry with timestamp."""
        self._ensure_cache_size_limit()
        self._stats_cache[key] = value
        self._cache_timestamps[key] = time.time()
    
    def add_entity(self, entity: Entity):
        """Index an entity."""
        self.entities_by_type[entity.type].add(entity.id)
        self.entities_by_name[entity.name.lower()].add(entity.id)
        self.invalidate_cache()
    
    def remove_entity(self, entity_id: str, entity_type: EntityType):
        """Remove entity from indexes."""
        self.entities_by_type[entity_type].discard(entity_id)
        # Clean up other indexes
        for name_set in self.entities_by_name.values():
            name_set.discard(entity_id)
        for scene_set in self.entities_by_scene.values():
            scene_set.discard(entity_id)
        self.invalidate_cache()
    
    def add_relationship(self, rel: Relationship):
        """Index a relationship."""
        self.relationships_by_type[rel.type].add((rel.source_id, rel.target_id))
        self.outgoing_edges[rel.source_id].add(rel.target_id)
        self.incoming_edges[rel.target_id].add(rel.source_id)
        self.invalidate_cache()
    
    def remove_relationship(self, source_id: str, target_id: str):
        """Remove relationship from indexes."""
        for rel_set in self.relationships_by_type.values():
            rel_set.discard((source_id, target_id))
        self.outgoing_edges[source_id].discard(target_id)
        self.incoming_edges[target_id].discard(source_id)
        self.invalidate_cache()

class NarrativeGraphEngine:
    """
    High-performance graph engine with thread safety and optimization.
    """
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self._lock = threading.RLock()
        
        # Core data structures
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        self.index = GraphIndex()
        
        # Change tracking for efficient updates
        self._changes = deque(maxlen=1000)  # Track last 1000 changes
        self._observers = weakref.WeakSet()  # Weak references to observers
        
        # Performance metrics
        self.metrics = {
            'total_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def __del__(self):
        """Cleanup resources and observers on destruction."""
        try:
            # Clear observers safely
            if hasattr(self, '_observers'):
                self._observers.clear()
            
            # Clear caches to free memory
            if hasattr(self, 'index'):
                self.index._stats_cache.clear()
                self.index._cache_timestamps.clear()
            
            # Clear main data structures
            if hasattr(self, 'entities'):
                self.entities.clear()
            if hasattr(self, 'relationships'):
                self.relationships.clear()
                
        except Exception:
            # Silently ignore cleanup errors to prevent issues during shutdown
            pass
    
    # Thread-safe entity operations
    def add_entity(self, name: str, entity_type: EntityType, **attributes) -> str:
        """Add or update an entity."""
        with self._lock:
            # First check if entity already exists by name and type
            existing_entity = None
            existing_id = None
            
            # Look for existing entity with same name and type
            for entity_id, entity in self.entities.items():
                if (entity.name.lower() == name.lower() and 
                    entity.type == entity_type):
                    existing_entity = entity
                    existing_id = entity_id
                    break
            
            if existing_entity:
                # Update existing entity
                existing_entity.attributes.update(attributes)
                existing_entity.mention_count += 1
                entity_id = existing_id
            else:
                # Create new entity
                entity_id = self._generate_entity_id(name, entity_type)
                entity = Entity(
                    id=entity_id,
                    name=name,
                    type=entity_type,
                    attributes=attributes,
                    first_appearance=datetime.now().isoformat(),
                    mention_count=1
                )
                self.entities[entity_id] = entity
                self.index.add_entity(entity)
            
            self._record_change('add_entity', entity_id)
            self._notify_observers('entity_added', entity_id)
            self.metrics['total_operations'] += 1
            
            return entity_id
    
    def clear(self):
        """Clear all graph data."""
        with self._lock:
            self.entities.clear()
            self.relationships.clear()
            self.index = GraphIndex()
            self.index.invalidate_cache()
            self._notify_observers('graph_cleared', None)
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity and all its relationships."""
        with self._lock:
            if entity_id not in self.entities:
                return False
            
            entity = self.entities[entity_id]
            
            # Remove all relationships involving this entity
            to_remove = []
            for (source, target), rel in self.relationships.items():
                if source == entity_id or target == entity_id:
                    to_remove.append((source, target))
            
            for key in to_remove:
                del self.relationships[key]
                self.index.remove_relationship(key[0], key[1])
            
            # Remove entity
            del self.entities[entity_id]
            self.index.remove_entity(entity_id, entity.type)
            
            self._record_change('remove_entity', entity_id)
            self._notify_observers('entity_removed', entity_id)
            self.metrics['total_operations'] += 1
            
            return True
    
    def add_relationship(self, source_id: str, target_id: str, 
                        rel_type: RelationType, **attributes) -> bool:
        """Add or strengthen a relationship."""
        with self._lock:
            if source_id not in self.entities or target_id not in self.entities:
                return False
            
            key = (source_id, target_id)
            
            if key in self.relationships:
                # Strengthen existing relationship
                rel = self.relationships[key]
                rel.weight += 0.1
                rel.attributes.update(attributes)
            else:
                # Create new relationship
                rel = Relationship(
                    source_id=source_id,
                    target_id=target_id,
                    type=rel_type,
                    attributes=attributes
                )
                self.relationships[key] = rel
                self.index.add_relationship(rel)
            
            self._record_change('add_relationship', key)
            self._notify_observers('relationship_added', key)
            self.metrics['total_operations'] += 1
            
            return True
    
    # High-performance queries
    def find_entities(self, entity_type: Optional[EntityType] = None,
                     name_pattern: Optional[str] = None,
                     min_importance: float = 0.0) -> List[Entity]:
        """Find entities matching criteria."""
        with self._lock:
            results = []
            
            # Use index for type filtering
            if entity_type:
                candidate_ids = self.index.entities_by_type[entity_type]
            else:
                candidate_ids = set(self.entities.keys())
            
            # Apply filters
            for entity_id in candidate_ids:
                entity = self.entities[entity_id]
                
                if name_pattern and name_pattern.lower() not in entity.name.lower():
                    continue
                
                if entity.importance_score < min_importance:
                    continue
                
                results.append(entity)
            
            return sorted(results, key=lambda e: e.importance_score, reverse=True)
    
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find shortest path between two entities using BFS."""
        if source_id not in self.entities or target_id not in self.entities:
            return None
        
        with self._lock:
            # BFS - consider both directions
            queue = deque([(source_id, [source_id])])
            visited = {source_id}
            
            while queue:
                current, path = queue.popleft()
                
                if current == target_id:
                    return path
                
                # Check both outgoing and incoming edges (treat as undirected)
                neighbors = set()
                neighbors.update(self.index.outgoing_edges[current])
                neighbors.update(self.index.incoming_edges[current])
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            
            return None
    
    def calculate_importance(self) -> Dict[str, float]:
        """Calculate importance scores using PageRank-like algorithm."""
        with self._lock:
            # Check cache using new cache management
            cached_result = self.index._get_cache_entry('importance')
            if cached_result is not None:
                self.metrics['cache_hits'] += 1
                return cached_result
            
            self.metrics['cache_misses'] += 1
            
            # Initialize scores
            scores = {entity_id: 1.0 for entity_id in self.entities}
            damping = 0.85
            iterations = 20
            
            for _ in range(iterations):
                new_scores = {}
                
                for entity_id in self.entities:
                    # Base score
                    score = (1 - damping)
                    
                    # Add contributions from incoming links
                    for source_id in self.index.incoming_edges[entity_id]:
                        out_degree = len(self.index.outgoing_edges[source_id])
                        if out_degree > 0:
                            score += damping * scores[source_id] / out_degree
                    
                    new_scores[entity_id] = score
                
                scores = new_scores
            
            # Update entity importance scores
            for entity_id, score in scores.items():
                self.entities[entity_id].importance_score = score
            
            # Cache results using new cache management
            self.index._set_cache_entry('importance', scores)
            self.index._cache_dirty = False
            
            return scores
    
    def find_communities(self) -> Dict[int, Set[str]]:
        """Find communities using Louvain-like algorithm."""
        with self._lock:
            # Simple community detection
            communities = {}
            community_id = 0
            visited = set()
            
            for entity_id in self.entities:
                if entity_id not in visited:
                    # BFS to find connected component
                    community = set()
                    queue = deque([entity_id])
                    
                    while queue:
                        current = queue.popleft()
                        if current in visited:
                            continue
                        
                        visited.add(current)
                        community.add(current)
                        
                        # Add neighbors
                        neighbors = (self.index.outgoing_edges[current] | 
                                   self.index.incoming_edges[current])
                        queue.extend(neighbors - visited)
                    
                    communities[community_id] = community
                    community_id += 1
            
            return communities
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        with self._lock:
            # Check cache using new cache management
            cached_result = self.index._get_cache_entry('stats')
            if cached_result is not None:
                self.metrics['cache_hits'] += 1
                return cached_result
            
            self.metrics['cache_misses'] += 1
            
            stats = {
                'total_entities': len(self.entities),
                'total_relationships': len(self.relationships),
                'entities_by_type': {
                    entity_type.name: len(ids) 
                    for entity_type, ids in self.index.entities_by_type.items()
                },
                'relationships_by_type': {
                    rel_type.name: len(rels)
                    for rel_type, rels in self.index.relationships_by_type.items()
                },
                'avg_connections': sum(len(edges) for edges in self.index.outgoing_edges.values()) / max(len(self.entities), 1),
                'density': len(self.relationships) / max(len(self.entities) * (len(self.entities) - 1), 1),
                'performance_metrics': self.metrics.copy()
            }
            
            # Cache results using new cache management
            self.index._set_cache_entry('stats', stats)
            self.index._cache_dirty = False
            
            return stats
    
    # Persistence
    def save(self) -> bool:
        """Save graph to disk."""
        try:
            with self._lock:
                data = {
                    'entities': [
                        {
                            'id': e.id,
                            'name': e.name,
                            'type': e.type.name,
                            'attributes': e.attributes,
                            'first_appearance': e.first_appearance,
                            'last_appearance': e.last_appearance,
                            'mention_count': e.mention_count,
                            'importance_score': e.importance_score
                        }
                        for e in self.entities.values()
                    ],
                    'relationships': [
                        {
                            'source_id': r.source_id,
                            'target_id': r.target_id,
                            'type': r.type.name,
                            'weight': r.weight,
                            'attributes': r.attributes,
                            'occurrences': r.occurrences
                        }
                        for r in self.relationships.values()
                    ],
                    'metrics': self.metrics
                }
                
                import os
                graph_file = os.path.join(self.project_path, '.narrative_graph.json')
                with open(graph_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                LOGGER.info(f"Saved graph with {len(self.entities)} entities")
                return True
                
        except Exception as e:
            LOGGER.error(f"Failed to save graph: {e}")
            return False
    
    def load(self) -> bool:
        """Load graph from disk."""
        try:
            import os
            graph_file = os.path.join(self.project_path, '.narrative_graph.json')
            
            if not os.path.exists(graph_file):
                return False
            
            with open(graph_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self._lock:
                # Clear existing data
                self.entities.clear()
                self.relationships.clear()
                self.index = GraphIndex()
                
                # Load entities
                for e_data in data.get('entities', []):
                    entity = Entity(
                        id=e_data['id'],
                        name=e_data['name'],
                        type=EntityType[e_data['type']],
                        attributes=e_data.get('attributes', {}),
                        first_appearance=e_data.get('first_appearance'),
                        last_appearance=e_data.get('last_appearance'),
                        mention_count=e_data.get('mention_count', 0),
                        importance_score=e_data.get('importance_score', 0.0)
                    )
                    self.entities[entity.id] = entity
                    self.index.add_entity(entity)
                
                # Load relationships
                for r_data in data.get('relationships', []):
                    rel = Relationship(
                        source_id=r_data['source_id'],
                        target_id=r_data['target_id'],
                        type=RelationType[r_data['type']],
                        weight=r_data.get('weight', 1.0),
                        attributes=r_data.get('attributes', {}),
                        occurrences=r_data.get('occurrences', [])
                    )
                    self.relationships[(rel.source_id, rel.target_id)] = rel
                    self.index.add_relationship(rel)
                
                # Load metrics
                self.metrics.update(data.get('metrics', {}))
                
                LOGGER.info(f"Loaded graph with {len(self.entities)} entities")
                return True
                
        except Exception as e:
            LOGGER.error(f"Failed to load graph: {e}")
            return False
    
    # Observer pattern for UI updates
    def register_observer(self, observer):
        """Register an observer for graph changes."""
        self._observers.add(observer)
    
    def _notify_observers(self, event: str, data: Any):
        """Notify all observers of a change."""
        for observer in self._observers:
            try:
                if hasattr(observer, 'on_graph_change'):
                    observer.on_graph_change(event, data)
            except Exception as e:
                LOGGER.debug(f"Observer notification failed: {e}")
    
    def _record_change(self, change_type: str, data: Any):
        """Record a change for undo/redo functionality."""
        self._changes.append({
            'type': change_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_entity_id(self, name: str, entity_type: EntityType) -> str:
        """Generate a unique entity ID."""
        base_id = f"{entity_type.name.lower()}_{name.lower().replace(' ', '_')}"
        
        # Ensure uniqueness
        if base_id not in self.entities:
            return base_id
        
        counter = 1
        while f"{base_id}_{counter}" in self.entities:
            counter += 1
        
        return f"{base_id}_{counter}"