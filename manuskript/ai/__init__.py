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
    from .narrative_graph import narrative_graph
    from . import adaptive_voice
    from . import text_analyzer
    from . import async_worker
    
    # Initialize async worker pool
    async_worker.get_ai_thread_pool()
    
    # Initialize each module
    narrative_graph.initialize()
    adaptive_voice.initialize()
    text_analyzer.initialize()
    
    # Preload heavy models if any AI features are enabled
    if any(settings.aiFeatures.values()):
        preload_models()
    
    LOGGER.info("AI features initialized with async support")

def preload_models():
    """
    Preload heavy ML models in background for better responsiveness.
    """
    try:
        from .narrative_graph.utils import preload_nlp_model
        
        # Check if narrative graph is enabled
        if settings.aiFeatures.get("narrativeGraphMemory", False):
            LOGGER.info("Preloading NLP models for narrative graph...")
            preload_nlp_model()
        
    except Exception as e:
        LOGGER.error(f"Failed to preload models: {e}")

def cleanup_ai_features():
    """
    Clean up AI features on application shutdown.
    This should be called when the application exits.
    """
    from . import async_worker
    
    # Unload heavy models to free memory
    try:
        from .narrative_graph.utils import unload_nlp_model
        unload_nlp_model()
    except Exception as e:
        LOGGER.error(f"Failed to unload models: {e}")
    
    # Clean up thread pool
    async_worker.cleanup_thread_pool()
    
    # Clear all AI hooks
    settings.clear_hooks()
    
    LOGGER.info("AI features cleaned up")