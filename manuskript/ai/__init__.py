#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
AI Features Module for Manuskript

This module contains the AI-powered features for Manuskript, including:
- Narrative Graph Memory
- Adaptive Voice Style
- And other AI-enhanced writing tools
"""

from manuskript import settings
import logging

LOGGER = logging.getLogger(__name__)

def initialize_ai_features():
    """
    Initialize and register all AI feature hooks.
    This should be called when the application starts.
    """
    # Import individual AI modules
    from . import narrative_graph
    from . import adaptive_voice
    
    # Initialize each module
    narrative_graph.initialize()
    adaptive_voice.initialize()
    
    LOGGER.info("AI features initialized")