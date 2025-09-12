#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Utility functions for the Narrative Graph module.

Handles NLP processing, entity extraction, and relationship analysis.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

LOGGER = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    spacy = None
    NLP_AVAILABLE = False
    LOGGER.info("spaCy not installed. Using fallback NLP methods.")

try:
    from fastcoref import spacy_component
    COREF_AVAILABLE = True
except ImportError:
    COREF_AVAILABLE = False
    LOGGER.info("fastcoref not installed. Coreference resolution disabled.")

# Global NLP model (loaded on demand)
_nlp_model = None
_model_loading = False
_model_load_failed = False

def get_nlp_model():
    """
    Get or load the spaCy NLP model with lazy loading and error caching.
    
    Returns:
        spaCy model or None if not available
    """
    global _nlp_model, _model_loading, _model_load_failed
    
    if not NLP_AVAILABLE:
        return None
    
    # Return cached model if already loaded
    if _nlp_model is not None:
        return _nlp_model
    
    # Don't retry if previous load failed
    if _model_load_failed:
        return None
    
    # Prevent concurrent loading attempts
    if _model_loading:
        LOGGER.debug("NLP model already loading, skipping...")
        return None
    
    _model_loading = True
    
    try:
        LOGGER.info("Loading spaCy model: en_core_web_sm (this may take a moment)...")
        
        # Try to load the model
        _nlp_model = spacy.load("en_core_web_sm")
        
        # Configure model for better performance
        _nlp_model.max_length = 1000000  # Handle longer texts
        
        # Add coreference resolution if available
        if COREF_AVAILABLE:
            try:
                _nlp_model.add_pipe("fastcoref")
                LOGGER.info("Added coreference resolution component")
            except Exception as e:
                LOGGER.warning(f"Failed to add coreference component: {e}")
        
        LOGGER.info("Successfully loaded spaCy model with all components")
        
    except OSError as e:
        LOGGER.warning("spaCy model 'en_core_web_sm' not found. "
                      "Install with: python -m spacy download en_core_web_sm")
        _model_load_failed = True
        _nlp_model = None
    except Exception as e:
        LOGGER.error(f"Failed to load spaCy model: {e}")
        _model_load_failed = True
        _nlp_model = None
    finally:
        _model_loading = False
    
    return _nlp_model

def preload_nlp_model():
    """
    Preload the NLP model in background (for warm startup).
    Should be called when AI features are first enabled.
    """
    from threading import Thread
    
    def load_model():
        try:
            model = get_nlp_model()
            if model:
                LOGGER.info("NLP model preloaded successfully")
            else:
                LOGGER.info("NLP model preload skipped (not available)")
        except Exception as e:
            LOGGER.error(f"Failed to preload NLP model: {e}")
    
    # Load model in background thread
    thread = Thread(target=load_model, daemon=True)
    thread.start()

def unload_nlp_model():
    """
    Unload the NLP model to free memory.
    Should be called when AI features are disabled.
    """
    global _nlp_model, _model_load_failed
    
    if _nlp_model is not None:
        LOGGER.info("Unloading spaCy NLP model")
        _nlp_model = None
        _model_load_failed = False  # Reset failure state

def process_doc_entities(doc, entities):
    """Helper function to process entities from a spaCy doc."""
    # First, try standard NER
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["characters"].append(ent.text)
        elif ent.label_ in ["GPE", "LOC", "FAC"]:
            entities["locations"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ == "TIME":
            entities["times"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        else:
            entities["other"].append(ent.text)
    
    # Also use syntactic analysis for proper nouns not caught by NER
    # This helps with fictional names and test data like "Character_0"
    for token in doc:
        # Proper nouns that are subjects are likely characters
        if token.pos_ == "PROPN" and token.dep_ in ["nsubj", "nsubjpass"]:
            if token.text not in entities["characters"]:
                entities["characters"].append(token.text)
        # Proper nouns that are direct objects with motion verbs might be locations
        elif token.pos_ == "PROPN" and token.dep_ == "dobj":
            # Check if the verb implies location (visit, enter, leave, etc.)
            if token.head.lemma_ in ["visit", "enter", "leave", "reach", "approach"]:
                if token.text not in entities["locations"]:
                    entities["locations"].append(token.text)
            # Otherwise it's likely a character being acted upon
            elif token.text not in entities["characters"]:
                entities["characters"].append(token.text)
        # Proper nouns after prepositions are likely places
        elif token.pos_ == "PROPN" and token.dep_ == "pobj":
            if token.text not in entities["locations"]:
                entities["locations"].append(token.text)
        # Other proper nouns in agent positions are likely characters
        elif token.pos_ == "PROPN" and token.dep_ in ["agent", "iobj"]:
            if token.text not in entities["characters"]:
                entities["characters"].append(token.text)
        
        # Also check for common nouns that are objects of location prepositions
        # This helps with lowercase locations like "castle", "forest", etc.
        elif token.pos_ == "NOUN" and token.dep_ == "pobj":
            # Check if preceded by location preposition
            if token.head.text.lower() in ["to", "at", "in", "from", "near", "by", "into", "through", "across"]:
                # Common location words in narratives
                if token.lemma_ in ["castle", "village", "forest", "mountain", "palace", "town", 
                                    "city", "house", "room", "garden", "tower", "dungeon", "cave",
                                    "river", "lake", "ocean", "street", "road", "path", "bridge",
                                    "valley", "hill", "field", "meadow", "desert", "island", "shore"]:
                    if token.text not in entities["locations"]:
                        entities["locations"].append(token.text)
    
    # Resolve coreferences if available
    if COREF_AVAILABLE and hasattr(doc, 'coref_chains'):
        for chain in doc.coref_chains:
            # Add coreference mentions to characters
            main_mention = chain.main
            if main_mention.text not in entities["characters"]:
                entities["characters"].append(main_mention.text)

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text.
    
    Args:
        text: Input text
        
    Returns:
        Dict with entity types as keys and lists of entities as values
    """
    entities = defaultdict(list)
    
    nlp = get_nlp_model()
    if nlp:
        # Check text length and process in chunks if needed
        max_length = nlp.max_length
        if len(text) > max_length:
            # Process text in chunks
            chunk_size = max_length - 1000  # Leave some buffer
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            for chunk in chunks:
                try:
                    doc = nlp(chunk)
                    process_doc_entities(doc, entities)
                except Exception as e:
                    LOGGER.warning(f"Failed to process chunk: {e}")
                    continue
        else:
            # Use spaCy for entity extraction
            try:
                doc = nlp(text)
                process_doc_entities(doc, entities)
            except Exception as e:
                LOGGER.warning(f"Failed to process text with spaCy: {e}")
                # Fall back to simple extraction
                entities = extract_entities_fallback(text)
    else:
        # Fallback: Simple regex-based extraction
        entities = extract_entities_fallback(text)
    
    # Deduplicate while preserving order
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))
    
    # Ensure required keys exist
    result = dict(entities)
    for key in ['characters', 'locations', 'relationships']:
        if key not in result:
            result[key] = []
    
    return result

def extract_entities_fallback(text: str) -> Dict[str, List[str]]:
    """
    Fallback entity extraction using NLTK when spaCy is unavailable.
    
    Args:
        text: Input text
        
    Returns:
        Dict with entity types and extracted entities
    """
    entities = defaultdict(list)
    
    try:
        import nltk
        # Download required data if not present (runs once)
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        
        # Tokenize and POS tag
        tokens = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        
        # Extract proper nouns (NNP, NNPS) and contextual nouns as entities
        for i, (word, pos) in enumerate(pos_tags):
            if pos in ['NNP', 'NNPS']:  # Proper nouns
                # Look at context to classify
                # If preceded by location preposition, it's likely a location
                if i > 0 and pos_tags[i-1][0].lower() in ['to', 'at', 'in', 'from', 'near', 'by', 'the']:
                    entities["locations"].append(word)
                # If preceded by verbs like 'visited', 'entered', 'left', it's likely a location
                elif i > 0 and pos_tags[i-1][0].lower() in ['visited', 'entered', 'left', 'reached', 'approached']:
                    entities["locations"].append(word)
                # If it's followed by a verb, it's likely a character (subject)
                elif i < len(pos_tags) - 1 and pos_tags[i+1][1].startswith('VB'):
                    entities["characters"].append(word)
                else:
                    # Default to character for narrative text
                    entities["characters"].append(word)
            elif pos in ['NN', 'NNS'] and i > 1:  # Common nouns with context
                # Check if preceded by "the" and a location preposition
                if (pos_tags[i-1][0].lower() == 'the' and 
                    pos_tags[i-2][0].lower() in ['to', 'at', 'in', 'from', 'near', 'by', 'into']):
                    # Common location words
                    if word.lower() in ['castle', 'village', 'forest', 'mountain', 'palace', 'town', 
                                       'city', 'house', 'room', 'garden', 'tower', 'dungeon', 'cave',
                                       'river', 'lake', 'ocean', 'street', 'road', 'path', 'bridge']:
                        entities["locations"].append(word)
                    
    except ImportError:
        # If NLTK is also not available, use a very simple approach
        # Just split on spaces and take capitalized words
        words = text.split()
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = word.strip('.,!?;:"')
            if clean_word and clean_word[0].isupper():
                # Check if preceded by location indicators
                if i > 0:
                    prev_word = words[i-1].lower().strip('.,!?;:"')
                    if prev_word in ['to', 'at', 'in', 'from', 'near', 'by', 'the', 'visited', 'entered', 'left', 'reached', 'approached']:
                        entities["locations"].append(clean_word)
                        continue
                # Default to character since that's most common in narratives
                entities["characters"].append(clean_word)
    
    # Ensure required keys exist
    result = dict(entities)
    for key in ['characters', 'locations', 'relationships']:
        if key not in result:
            result[key] = []
    
    return result

def analyze_relationships(text: str, entities: Dict[str, List[str]]) -> List[Tuple[str, str, str]]:
    """
    Analyze relationships between entities in the text.
    
    Args:
        text: Input text
        entities: Previously extracted entities
        
    Returns:
        List of (source, relationship, target) tuples
    """
    relationships = []
    
    nlp = get_nlp_model()
    if nlp:
        doc = nlp(text)
        
        # Use dependency parsing to find relationships
        for token in doc:
            # Look for verbs that indicate relationships
            if token.pos_ == "VERB":
                # Find subject and object
                subj = None
                obj = None
                
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subj = child.text
                    elif child.dep_ in ["dobj", "pobj", "attr"]:
                        obj = child.text
                
                if subj and obj:
                    # Check if both are entities
                    if (subj in entities.get("characters", []) and 
                        obj in entities.get("characters", [])):
                        relationships.append((subj, token.lemma_, obj))
    else:
        # Fallback: Pattern-based relationship extraction
        relationships = analyze_relationships_fallback(text, entities)
    
    return relationships

def analyze_relationships_fallback(text: str, entities: Dict[str, List[str]]) -> List[Tuple[str, str, str]]:
    """
    Fallback relationship extraction using patterns.
    
    Args:
        text: Input text
        entities: Previously extracted entities
        
    Returns:
        List of (source, relationship, target) tuples
    """
    relationships = []
    characters = entities.get("characters", [])
    
    # Common relationship patterns
    patterns = [
        (r'(\w+)\s+(?:loves?|adores?|cares? for)\s+(\w+)', 'loves'),
        (r'(\w+)\s+(?:hates?|despises?|loathes?)\s+(\w+)', 'hates'),
        (r'(\w+)\s+(?:knows?|meets?|encounters?)\s+(\w+)', 'knows'),
        (r'(\w+)\s+(?:helps?|assists?|aids?)\s+(\w+)', 'helps'),
        (r'(\w+)\s+(?:fights?|battles?|confronts?)\s+(\w+)', 'fights'),
        (r'(\w+)\s+(?:talks? to|speaks? to|tells?)\s+(\w+)', 'talks_to'),
        (r'(\w+)\s+and\s+(\w+)', 'related_to'),
    ]
    
    for pattern, rel_type in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            source, target = match.groups()
            # Check if both are recognized characters
            if source in characters and target in characters:
                relationships.append((source, rel_type, target))
    
    return relationships

def detect_plot_points(text: str) -> List[Dict[str, Any]]:
    """
    Detect potential plot points or story beats in the text.
    
    Args:
        text: Input text
        
    Returns:
        List of plot point dictionaries
    """
    plot_points = []
    
    # Keywords that often indicate plot points
    plot_keywords = {
        'conflict': ['fight', 'argue', 'conflict', 'battle', 'confront', 'clash'],
        'revelation': ['realize', 'discover', 'reveal', 'uncover', 'learn', 'find out'],
        'decision': ['decide', 'choose', 'determine', 'resolve'],
        'transformation': ['change', 'transform', 'become', 'turn into'],
        'journey': ['travel', 'journey', 'arrive', 'depart', 'leave', 'return'],
        'emotion': ['cry', 'laugh', 'scream', 'sob', 'smile'],
        'death': ['die', 'death', 'kill', 'murder', 'perish'],
        'love': ['kiss', 'embrace', 'marry', 'propose', 'love']
    }
    
    sentences = text.split('.')
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        
        for plot_type, keywords in plot_keywords.items():
            if any(keyword in sentence_lower for keyword in keywords):
                plot_points.append({
                    'type': plot_type,
                    'text': sentence.strip(),
                    'position': i / max(len(sentences), 1),  # Relative position in text
                    'keywords': [kw for kw in keywords if kw in sentence_lower]
                })
                break
    
    return plot_points

def calculate_sentiment(text: str) -> Dict[str, float]:
    """
    Calculate sentiment scores for the text.
    
    Args:
        text: Input text
        
    Returns:
        Dict with sentiment scores
    """
    sentiment = {
        'positive': 0.0,
        'negative': 0.0,
        'neutral': 0.0
    }
    
    # Simple word-based sentiment (can be enhanced with ML models)
    positive_words = set(['happy', 'joy', 'love', 'excellent', 'wonderful', 
                         'beautiful', 'amazing', 'great', 'fantastic', 'good'])
    negative_words = set(['sad', 'angry', 'hate', 'terrible', 'awful', 
                         'horrible', 'bad', 'disgusting', 'evil', 'pain'])
    
    words = text.lower().split()
    total_words = len(words)
    
    if total_words > 0:
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        sentiment['positive'] = pos_count / total_words
        sentiment['negative'] = neg_count / total_words
        sentiment['neutral'] = 1.0 - (sentiment['positive'] + sentiment['negative'])
    
    return sentiment

def find_dialogue(text: str) -> List[Dict[str, str]]:
    """
    Extract dialogue from the text.
    
    Args:
        text: Input text
        
    Returns:
        List of dialogue dictionaries with speaker and text
    """
    dialogue = []
    
    # Pattern for dialogue with attribution
    pattern1 = r'"([^"]+)"\s+(?:said|asked|replied|whispered|shouted|muttered)\s+([A-Z][a-z]+)'
    matches = re.finditer(pattern1, text)
    
    for match in matches:
        dialogue.append({
            'text': match.group(1),
            'speaker': match.group(2),
            'type': 'attributed'
        })
    
    # Pattern for standalone dialogue
    pattern2 = r'"([^"]+)"'
    all_quotes = re.finditer(pattern2, text)
    
    for match in all_quotes:
        quote_text = match.group(1)
        # Check if this quote was already captured with attribution
        if not any(d['text'] == quote_text for d in dialogue):
            dialogue.append({
                'text': quote_text,
                'speaker': 'unknown',
                'type': 'unattributed'
            })
    
    return dialogue

def check_dependencies():
    """
    Check if required NLP dependencies are installed.
    
    Returns:
        Dict with availability status of dependencies
    """
    status = {
        'spacy': NLP_AVAILABLE,
        'fastcoref': COREF_AVAILABLE,
        'model_loaded': get_nlp_model() is not None
    }
    
    if not status['spacy']:
        LOGGER.info("To enable advanced NLP features, install spaCy: pip install spacy")
    
    if status['spacy'] and not status['model_loaded']:
        LOGGER.info("Download the English model: python -m spacy download en_core_web_sm")
    
    if not status['fastcoref']:
        LOGGER.info("For coreference resolution, install: pip install fastcoref")
    
    return status

def install_dependencies():
    """
    Attempt to install missing dependencies.
    Should be called when user enables AI features.
    """
    import subprocess
    import sys
    
    packages_to_install = []
    
    if not NLP_AVAILABLE:
        packages_to_install.append('spacy')
    
    if not COREF_AVAILABLE:
        packages_to_install.append('fastcoref')
    
    # Check for NetworkX
    try:
        import networkx
    except ImportError:
        packages_to_install.append('networkx')
    
    if packages_to_install:
        LOGGER.info(f"Installing packages: {', '.join(packages_to_install)}")
        
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'] + packages_to_install
            )
            
            # Download spaCy model if spaCy was just installed
            if 'spacy' in packages_to_install:
                LOGGER.info("Downloading spaCy English model...")
                subprocess.check_call([
                    sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'
                ])
            
            LOGGER.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Failed to install dependencies: {e}")
            return False
    
    return True