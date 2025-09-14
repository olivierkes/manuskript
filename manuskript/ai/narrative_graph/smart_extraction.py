#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Smart Entity Extraction that uses existing character/world models first.
Only uses NLP as fallback for unrecognized entities.
"""

import logging
import re
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter

LOGGER = logging.getLogger(__name__)

class SmartEntityExtractor:
    """Extract entities using existing models + smart NLP fallback."""
    
    def __init__(self, main_window):
        """Initialize with access to main window models."""
        self.main_window = main_window
        self.known_characters = set()
        self.known_locations = set()
        self.character_aliases = {}  # Map aliases to canonical names
        self.load_existing_entities()
        
    def load_existing_entities(self):
        """Load characters and locations from existing models."""
        try:
            # Load characters from character model
            if hasattr(self.main_window, 'mdlCharacter'):
                for i in range(self.main_window.mdlCharacter.rowCount()):
                    char_index = self.main_window.mdlCharacter.index(i, 0)
                    char_name = self.main_window.mdlCharacter.data(char_index)
                    if char_name:
                        self.known_characters.add(char_name)
                        # Also track common variations
                        self._add_name_variations(char_name)
            
            # Load locations from world model
            if hasattr(self.main_window, 'mdlWorld'):
                self._extract_world_items(self.main_window.mdlWorld.invisibleRootItem())
                
            LOGGER.info(f"Loaded {len(self.known_characters)} characters, {len(self.known_locations)} locations")
            
        except Exception as e:
            LOGGER.error(f"Failed to load existing entities: {e}")
    
    def _add_name_variations(self, full_name: str):
        """Add common variations of a character name."""
        parts = full_name.split()
        if len(parts) > 1:
            # First name only
            self.character_aliases[parts[0]] = full_name
            # Last name only (if not too short)
            if len(parts[-1]) > 3:
                self.character_aliases[parts[-1]] = full_name
            # Mr./Mrs./Dr. + Last name
            for title in ["Mr.", "Mrs.", "Ms.", "Dr."]:
                self.character_aliases[f"{title} {parts[-1]}"] = full_name
    
    def _extract_world_items(self, parent_item, parent_type=""):
        """Recursively extract world items (locations, etc)."""
        for i in range(parent_item.rowCount()):
            item = parent_item.child(i, 0)
            if item:
                name = item.text()
                # Determine if this is a location based on parent
                if parent_type in ["Places", "Locations"] or "place" in name.lower():
                    self.known_locations.add(name)
                elif name in ["Places", "Locations"]:
                    # This is a category, recurse with type
                    self._extract_world_items(item, name)
                else:
                    # Recurse to find nested locations
                    self._extract_world_items(item, parent_type)
    
    def extract_from_text(self, text: str) -> Dict[str, any]:
        """
        Extract entities and relationships from text.
        Returns dict with characters, locations, and interactions.
        """
        result = {
            "characters": set(),
            "locations": set(),
            "interactions": [],  # List of (char1, action, char2) tuples
            "character_mentions": Counter(),  # Track mention frequency
            "scene_participants": set(),  # Characters active in this scene
        }
        
        # First pass: Find known entities
        sentences = self._split_sentences(text)
        for sentence in sentences:
            # Find known characters
            for char in self.known_characters:
                if self._name_in_text(char, sentence):
                    result["characters"].add(char)
                    result["character_mentions"][char] += 1
                    result["scene_participants"].add(char)
            
            # Check aliases
            for alias, canonical in self.character_aliases.items():
                if self._name_in_text(alias, sentence):
                    result["characters"].add(canonical)
                    result["character_mentions"][canonical] += 1
                    result["scene_participants"].add(canonical)
            
            # Find known locations
            for loc in self.known_locations:
                if self._name_in_text(loc, sentence):
                    result["locations"].add(loc)
        
        # Second pass: Extract interactions between known characters
        result["interactions"] = self._extract_interactions(text, result["characters"])
        
        # Third pass: Use NLP only for unrecognized proper nouns
        # (This is where we'd add smart NLP for finding NEW entities)
        
        return result
    
    def _name_in_text(self, name: str, text: str) -> bool:
        """Check if a name appears in text (case-insensitive, word boundary)."""
        pattern = r'\b' + re.escape(name) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_interactions(self, text: str, characters: Set[str]) -> List[Tuple[str, str, str]]:
        """
        Extract character interactions from text.
        Returns list of (character1, action, character2) tuples.
        """
        interactions = []
        
        # Action verbs that indicate interaction
        INTERACTION_VERBS = {
            'said to', 'told', 'asked', 'answered', 'spoke to', 'talked to',
            'looked at', 'glanced at', 'stared at', 'watched',
            'gave', 'handed', 'passed', 'showed',
            'helped', 'assisted', 'aided',
            'fought', 'attacked', 'defended', 'protected',
            'hugged', 'kissed', 'embraced', 'touched',
            'followed', 'led', 'accompanied', 'joined',
            'met', 'encountered', 'found', 'discovered',
            'saved', 'rescued', 'freed',
            'betrayed', 'deceived', 'tricked',
            'loved', 'hated', 'feared', 'admired'
        }
        
        # Check each sentence for interactions
        sentences = self._split_sentences(text)
        for sentence in sentences:
            # Find all characters mentioned in this sentence with their positions
            char_positions = []
            for char in characters:
                if self._name_in_text(char, sentence):
                    # Find position of character in sentence
                    pattern = r'\b' + re.escape(char) + r'\b'
                    match = re.search(pattern, sentence, re.IGNORECASE)
                    if match:
                        char_positions.append((match.start(), char))
            
            # Sort characters by their position in the sentence
            char_positions.sort(key=lambda x: x[0])
            chars_in_sentence = [char for pos, char in char_positions]
            
            # If 2+ characters in sentence, check for interaction verbs
            if len(chars_in_sentence) >= 2:
                sentence_lower = sentence.lower()
                for verb in INTERACTION_VERBS:
                    if verb in sentence_lower:
                        # Find verb position to determine interaction direction
                        verb_pos = sentence_lower.find(verb)
                        char1_pos = char_positions[0][0]
                        char2_pos = char_positions[1][0]
                        
                        # Character before verb acts on character after verb
                        if char1_pos < verb_pos < char2_pos:
                            interactions.append((chars_in_sentence[0], verb, chars_in_sentence[1]))
                        elif char2_pos < verb_pos < char1_pos:
                            interactions.append((chars_in_sentence[1], verb, chars_in_sentence[0]))
                        else:
                            # Default to first mentioned acting on second
                            interactions.append((chars_in_sentence[0], verb, chars_in_sentence[1]))
                        break
        
        return interactions
    
    def analyze_scene_flow(self, outline_model) -> Dict[str, any]:
        """
        Analyze character presence and flow across scenes/chapters.
        Returns timeline and presence data.
        """
        scene_data = {
            "character_timeline": defaultdict(list),  # char -> list of scenes
            "scene_characters": defaultdict(set),  # scene -> set of chars
            "character_frequency": Counter(),  # How often each character appears
            "interaction_matrix": defaultdict(Counter),  # char -> {other_char: count}
            "location_usage": Counter(),  # How often each location is used
        }
        
        # Analyze each scene in the outline
        def analyze_item(item, path=""):
            from manuskript.enums import Outline
            
            # Get item title for path
            title = item.data(Outline.title.value)
            if title:
                current_path = f"{path}/{title}" if path else title
            else:
                current_path = path
            
            # Get text content
            text = item.data(Outline.text.value)
            if text:
                # Extract entities from this scene
                entities = self.extract_from_text(text)
                
                # Track character presence
                for char in entities["scene_participants"]:
                    scene_data["character_timeline"][char].append(current_path)
                    scene_data["scene_characters"][current_path].add(char)
                    scene_data["character_frequency"][char] += 1
                
                # Track interactions
                for char1, action, char2 in entities["interactions"]:
                    scene_data["interaction_matrix"][char1][char2] += 1
                    scene_data["interaction_matrix"][char2][char1] += 1
                
                # Track location usage
                for loc in entities["locations"]:
                    scene_data["location_usage"][loc] += 1
            
            # Recurse through children
            for i in range(item.childCount()):
                analyze_item(item.child(i), current_path)
        
        # Start analysis from root
        if outline_model:
            root = outline_model.rootItem
            analyze_item(root)
        
        return scene_data
    
    def get_existing_characters(self):
        """Get existing characters from the character model."""
        characters = {}
        if hasattr(self.main_window, 'mdlCharacter'):
            from manuskript.enums import Character
            for i in range(self.main_window.mdlCharacter.rowCount()):
                char_id = str(i)
                char_name = self.main_window.mdlCharacter.data(
                    self.main_window.mdlCharacter.index(i, Character.name.value)
                )
                char_motivation = self.main_window.mdlCharacter.data(
                    self.main_window.mdlCharacter.index(i, Character.motivation.value)
                ) or ""
                
                if char_name:
                    characters[char_id] = {
                        'name': char_name,
                        'motivation': char_motivation
                    }
        return characters
    
    def get_existing_locations(self):
        """Get existing locations from the world model."""
        locations = {}
        if hasattr(self.main_window, 'mdlWorld'):
            # Recursively extract locations with metadata
            def extract_locations(item, parent_path=""):
                for i in range(item.rowCount()):
                    child = item.child(i, 0)
                    if child:
                        loc_name = child.text()
                        loc_id = f"{parent_path}/{loc_name}" if parent_path else loc_name
                        
                        # Get description from second column if available
                        desc_item = item.child(i, 1)
                        description = desc_item.text() if desc_item else ""
                        
                        locations[loc_id] = {
                            'name': loc_name,
                            'description': description
                        }
                        extract_locations(child, loc_id)
            
            root = self.main_window.mdlWorld.invisibleRootItem()
            extract_locations(root)
        
        return locations
    
    def analyze_character_interactions(self, text: str, characters: List[str]) -> List[Dict]:
        """Analyze character interactions in text."""
        interactions = []
        
        # Use the existing _extract_interactions method
        raw_interactions = self._extract_interactions(text, set(characters))
        
        # Convert to dict format
        for char1, action, char2 in raw_interactions:
            interactions.append({
                'character1': char1,
                'character2': char2,
                'type': action
            })
        
        return interactions
    
    def get_insights(self, scene_data: Dict) -> List[str]:
        """
        Generate actionable insights from scene analysis.
        Returns list of insight strings.
        """
        insights = []
        
        # Find unused characters
        all_chars = self.known_characters
        used_chars = set(scene_data["character_frequency"].keys())
        unused = all_chars - used_chars
        if unused:
            insights.append(f"⚠️ Unused characters: {', '.join(sorted(unused))}")
        
        # Find characters who never interact
        if len(used_chars) > 1:
            no_interaction = []
            chars_list = sorted(used_chars)
            for i, char1 in enumerate(chars_list):
                for char2 in chars_list[i+1:]:
                    if scene_data["interaction_matrix"][char1][char2] == 0:
                        no_interaction.append((char1, char2))
            
            if no_interaction and len(no_interaction) <= 5:
                insights.append("💡 Characters who never interact:")
                for c1, c2 in no_interaction[:5]:
                    insights.append(f"  • {c1} ↔ {c2}")
        
        # Find underused characters
        if scene_data["character_frequency"]:
            avg_appearances = sum(scene_data["character_frequency"].values()) / len(scene_data["character_frequency"])
            underused = [char for char, count in scene_data["character_frequency"].items() 
                        if count < avg_appearances * 0.3]
            if underused:
                insights.append(f"📊 Underused characters (appear rarely): {', '.join(underused)}")
        
        # Find overused character pairs
        if scene_data["interaction_matrix"]:
            all_interactions = []
            for char1, others in scene_data["interaction_matrix"].items():
                for char2, count in others.items():
                    if char1 < char2:  # Avoid duplicates
                        all_interactions.append((count, char1, char2))
            
            if all_interactions:
                all_interactions.sort(reverse=True)
                if len(all_interactions) > 1:
                    # Check if top pair has way more interactions than others
                    top_count = all_interactions[0][0]
                    avg_count = sum(c for c, _, _ in all_interactions[1:]) / len(all_interactions[1:]) if len(all_interactions) > 1 else 0
                    if avg_count > 0 and top_count > avg_count * 3:
                        insights.append(f"🔄 Most frequent interaction: {all_interactions[0][1]} ↔ {all_interactions[0][2]} ({top_count} times)")
        
        # Find unused locations
        all_locs = self.known_locations
        used_locs = set(scene_data["location_usage"].keys())
        unused_locs = all_locs - used_locs
        if unused_locs:
            insights.append(f"📍 Unused locations: {', '.join(sorted(unused_locs))}")
        
        return insights