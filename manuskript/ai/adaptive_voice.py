#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Adaptive Voice Style Module

This module learns and adapts to your writing style, providing:
- Style consistency suggestions
- Voice matching for different characters
- Tone analysis and recommendations
"""

from manuskript import settings
import logging
import re
from collections import defaultdict

LOGGER = logging.getLogger(__name__)

# Store style patterns
style_patterns = {
    "sentence_lengths": [],
    "word_frequencies": defaultdict(int),
    "punctuation_usage": defaultdict(int),
    "paragraph_lengths": [],
    "vocabulary_complexity": 0,
    "character_voices": {}
}

def initialize():
    """
    Initialize the Adaptive Voice Style module and register hooks.
    """
    # Register hooks for text analysis with feature_key
    settings.register_hook("text_changed", analyze_writing_style, feature_key="adaptiveVoiceStyle", priority=15)
    settings.register_hook("after_load", load_style_profile, feature_key="adaptiveVoiceStyle", priority=10)
    settings.register_hook("before_save", save_style_profile, feature_key="adaptiveVoiceStyle", priority=10)
    
    LOGGER.info("Adaptive Voice Style module initialized")

def analyze_writing_style(text, index, editor):
    """
    Analyze the writing style of the provided text.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        # Analyze sentence structure
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if sentence.strip():
                style_patterns["sentence_lengths"].append(len(sentence.split()))
        
        # Analyze word usage
        words = text.lower().split()
        for word in words:
            # Clean punctuation
            word = re.sub(r'[^\w\s]', '', word)
            if word:
                style_patterns["word_frequencies"][word] += 1
        
        # Analyze punctuation patterns
        for char in text:
            if char in ',.;:!?"\'()-':
                style_patterns["punctuation_usage"][char] += 1
        
        # Analyze paragraph structure
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                style_patterns["paragraph_lengths"].append(len(para.split()))
        
        LOGGER.debug("Writing style analysis completed")
        
    except Exception as e:
        LOGGER.error(f"Failed to analyze writing style: {e}")

def load_style_profile(project_path, main_window):
    """
    Load the style profile when a project is opened.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        import json
        import os
        
        style_file = os.path.join(os.path.dirname(project_path), ".style_profile.json")
        if os.path.exists(style_file):
            with open(style_file, 'r') as f:
                global style_patterns
                loaded_patterns = json.load(f)
                # Convert defaultdicts back
                style_patterns["word_frequencies"] = defaultdict(int, loaded_patterns.get("word_frequencies", {}))
                style_patterns["punctuation_usage"] = defaultdict(int, loaded_patterns.get("punctuation_usage", {}))
                style_patterns["sentence_lengths"] = loaded_patterns.get("sentence_lengths", [])
                style_patterns["paragraph_lengths"] = loaded_patterns.get("paragraph_lengths", [])
                style_patterns["vocabulary_complexity"] = loaded_patterns.get("vocabulary_complexity", 0)
                style_patterns["character_voices"] = loaded_patterns.get("character_voices", {})
                
                LOGGER.info(f"Loaded style profile from {style_file}")
                
    except Exception as e:
        LOGGER.error(f"Failed to load style profile: {e}")

def save_style_profile(project_path, main_window):
    """
    Save the style profile when the project is saved.
    """
    # No need to check feature flag - handled by hook system
    
    try:
        import json
        import os
        
        style_file = os.path.join(os.path.dirname(project_path), ".style_profile.json")
        
        # Convert defaultdicts to regular dicts for JSON serialization
        save_patterns = {
            "sentence_lengths": style_patterns["sentence_lengths"][-1000:],  # Keep last 1000
            "word_frequencies": dict(style_patterns["word_frequencies"]),
            "punctuation_usage": dict(style_patterns["punctuation_usage"]),
            "paragraph_lengths": style_patterns["paragraph_lengths"][-500:],  # Keep last 500
            "vocabulary_complexity": calculate_vocabulary_complexity(),
            "character_voices": style_patterns["character_voices"]
        }
        
        with open(style_file, 'w') as f:
            json.dump(save_patterns, f, indent=2)
            LOGGER.debug(f"Saved style profile to {style_file}")
            
    except Exception as e:
        LOGGER.error(f"Failed to save style profile: {e}")

def calculate_vocabulary_complexity():
    """
    Calculate a simple vocabulary complexity score.
    """
    if not style_patterns["word_frequencies"]:
        return 0
    
    # Simple metric: unique words / total words
    unique_words = len(style_patterns["word_frequencies"])
    total_words = sum(style_patterns["word_frequencies"].values())
    
    if total_words == 0:
        return 0
    
    return unique_words / total_words

def get_style_suggestions(text):
    """
    Provide style suggestions based on the learned patterns.
    
    Args:
        text: The text to analyze
        
    Returns:
        list: Style suggestions
    """
    if not settings.aiFeatures.get("adaptiveVoiceStyle", False):
        return []
    
    suggestions = []
    
    # Analyze current text
    sentences = re.split(r'[.!?]+', text)
    current_sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    
    if current_sentence_lengths and style_patterns["sentence_lengths"]:
        avg_current = sum(current_sentence_lengths) / len(current_sentence_lengths)
        avg_style = sum(style_patterns["sentence_lengths"]) / len(style_patterns["sentence_lengths"])
        
        if abs(avg_current - avg_style) > 5:
            if avg_current > avg_style:
                suggestions.append("Your sentences are longer than your usual style. Consider breaking them up.")
            else:
                suggestions.append("Your sentences are shorter than your usual style. Consider adding more detail.")
    
    return suggestions

def match_character_voice(character_name, text):
    """
    Check if the text matches the established voice for a character.
    
    Args:
        character_name: Name of the character
        text: Dialogue or narration to check
        
    Returns:
        dict: Voice matching analysis
    """
    if not settings.aiFeatures.get("adaptiveVoiceStyle", False):
        return {}
    
    if character_name not in style_patterns["character_voices"]:
        # Initialize character voice profile
        style_patterns["character_voices"][character_name] = {
            "vocabulary": defaultdict(int),
            "sentence_patterns": []
        }
    
    # Update character voice profile
    words = text.lower().split()
    for word in words:
        word = re.sub(r'[^\w\s]', '', word)
        if word:
            style_patterns["character_voices"][character_name]["vocabulary"][word] += 1
    
    return {
        "character": character_name,
        "consistency": "analyzing..."
    }