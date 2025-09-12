#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
AI Features Module for Manuskript

This module contains the AI-powered features for Manuskript, including:
- Narrative Graph Memory
- Adaptive Voice Style
- Text Analysis with async processing
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
    from . import text_analyzer
    from . import async_worker
    
    # Initialize async worker pool
    async_worker.get_ai_thread_pool()
    
    # Initialize each module
    narrative_graph.initialize()
    adaptive_voice.initialize()
    text_analyzer.initialize()
    
    LOGGER.info("AI features initialized with async support")

def cleanup_ai_features():
    """
    Clean up AI features on application shutdown.
    This should be called when the application exits.
    """
    from . import async_worker
    
    # Clean up thread pool
    async_worker.cleanup_thread_pool()
    
    # Clear all AI hooks
    settings.clear_hooks()
    
    LOGGER.info("AI features cleaned up")