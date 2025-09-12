#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Narrative Graph Memory Module

Advanced story tracking using NetworkX graphs and spaCy NLP.
"""

from .narrative_graph import (
    initialize,
    on_project_loaded,
    on_project_save,
    on_text_changed,
    on_character_changed,
    get_context_for_scene,
    suggest_consistency_check
)

from .graph_storage import (
    GraphStorage,
    save_graph,
    load_graph
)

from .utils import (
    extract_entities,
    analyze_relationships,
    detect_plot_points
)

__all__ = [
    'initialize',
    'on_project_loaded',
    'on_project_save',
    'on_text_changed',
    'on_character_changed',
    'get_context_for_scene',
    'suggest_consistency_check',
    'GraphStorage',
    'save_graph',
    'load_graph',
    'extract_entities',
    'analyze_relationships',
    'detect_plot_points'
]