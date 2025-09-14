#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Text Analyzer Module - Example of CPU-heavy AI processing

Demonstrates how to use async processing for intensive AI tasks
that would otherwise block the UI.
"""

from manuskript import settings
from manuskript.ai.async_worker import async_hook, run_async, WorkerSignals
import logging
import time
import re
from typing import Dict, List, Any

LOGGER = logging.getLogger(__name__)

def initialize():
    """
    Initialize the Text Analyzer module and register async hooks.
    """
    # Register CPU-heavy text analysis with async decorator
    decorated_analyze = async_hook(cpu_heavy=True)(analyze_text_heavy)
    settings.register_hook(
        "text_changed", 
        decorated_analyze, 
        feature_key="narrativeGraphMemory",
        priority=20  # Lower priority for heavy processing
    )
    
    LOGGER.info("Text Analyzer module initialized with async processing")

@async_hook(cpu_heavy=True)
def analyze_text_heavy(text: str, index, editor, **kwargs) -> Dict[str, Any]:
    """
    Perform CPU-intensive text analysis.
    This runs in a background thread to avoid blocking the UI.
    
    Args:
        text: The text to analyze
        index: The model index
        editor: The text editor widget
        **kwargs: May include _worker_signals for progress reporting
        
    Returns:
        Analysis results dictionary
    """
    # Get worker signals if available for progress reporting
    signals = kwargs.get('_worker_signals')
    
    try:
        if signals:
            signals.status.emit("Starting text analysis...")
            signals.progress.emit(0)
        
        results = {
            "word_count": 0,
            "sentence_count": 0,
            "readability_score": 0,
            "sentiment": "neutral",
            "key_themes": [],
            "character_mentions": {},
            "pacing": "normal"
        }
        
        # Simulate CPU-heavy processing
        # In real implementation, this would be actual NLP/ML processing
        
        # Step 1: Basic text statistics (20%)
        if signals:
            signals.status.emit("Analyzing text statistics...")
            signals.progress.emit(20)
        
        words = text.split()
        results["word_count"] = len(words)
        
        sentences = re.split(r'[.!?]+', text)
        results["sentence_count"] = len([s for s in sentences if s.strip()])
        
        # Simulate processing time
        time.sleep(0.1)  # In real code, remove this
        
        # Step 2: Readability analysis (40%)
        if signals:
            signals.status.emit("Calculating readability...")
            signals.progress.emit(40)
        
        if results["sentence_count"] > 0:
            avg_words_per_sentence = results["word_count"] / results["sentence_count"]
            # Simplified Flesch Reading Ease approximation
            results["readability_score"] = max(0, min(100, 
                206.835 - 1.015 * avg_words_per_sentence))
        
        time.sleep(0.1)  # Simulate processing
        
        # Step 3: Sentiment analysis (60%)
        if signals:
            signals.status.emit("Analyzing sentiment...")
            signals.progress.emit(60)
        
        # Simple sentiment based on word presence (placeholder)
        positive_words = ['happy', 'joy', 'love', 'excellent', 'wonderful']
        negative_words = ['sad', 'angry', 'hate', 'terrible', 'awful']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            results["sentiment"] = "positive"
        elif neg_count > pos_count:
            results["sentiment"] = "negative"
        else:
            results["sentiment"] = "neutral"
        
        time.sleep(0.1)  # Simulate processing
        
        # Step 4: Character extraction (80%)
        if signals:
            signals.status.emit("Identifying characters...")
            signals.progress.emit(80)
        
        # Find capitalized words that might be character names
        potential_names = re.findall(r'\b[A-Z][a-z]+\b', text)
        for name in potential_names:
            if name not in results["character_mentions"]:
                results["character_mentions"][name] = 0
            results["character_mentions"][name] += 1
        
        time.sleep(0.1)  # Simulate processing
        
        # Step 5: Pacing analysis (100%)
        if signals:
            signals.status.emit("Analyzing pacing...")
            signals.progress.emit(90)
        
        if results["sentence_count"] > 0:
            avg_sentence_length = results["word_count"] / results["sentence_count"]
            if avg_sentence_length < 10:
                results["pacing"] = "fast"
            elif avg_sentence_length > 20:
                results["pacing"] = "slow"
            else:
                results["pacing"] = "normal"
        
        # Final progress
        if signals:
            signals.status.emit("Analysis complete!")
            signals.progress.emit(100)
        
        LOGGER.debug(f"Text analysis complete: {results}")
        
        # Store results for later use
        store_analysis_results(results)
        
        return results
        
    except Exception as e:
        LOGGER.error(f"Text analysis failed: {e}")
        if signals:
            signals.status.emit(f"Analysis failed: {str(e)}")
        raise

def store_analysis_results(results: Dict[str, Any]):
    """
    Store analysis results for future reference.
    This could be extended to save to a database or file.
    """
    # For now, just log the results
    LOGGER.info(f"Storing analysis results: word_count={results['word_count']}, "
                f"sentiment={results['sentiment']}, pacing={results['pacing']}")

def analyze_selection_async(text: str, callback: callable = None):
    """
    Public API for analyzing selected text asynchronously.
    
    Args:
        text: The text to analyze
        callback: Optional callback to receive results
    """
    def on_result(results):
        LOGGER.info(f"Analysis completed: {results}")
        if callback:
            callback(results)
    
    def on_error(error_info):
        LOGGER.error(f"Analysis failed: {error_info[2]}")
    
    def on_progress(value):
        LOGGER.debug(f"Analysis progress: {value}%")
    
    # Run analysis in background
    run_async(
        analyze_text_heavy,
        text,
        None,  # index
        None,  # editor
        on_result=on_result,
        on_error=on_error,
        on_progress=on_progress
    )

class TextAnalysisWidget:
    """
    Example widget that could display real-time analysis results.
    This would be integrated into the Manuskript UI.
    """
    
    def __init__(self):
        self.current_analysis = None
        self.is_analyzing = False
    
    def start_analysis(self, text: str):
        """Start analyzing text and update UI with progress."""
        if self.is_analyzing:
            LOGGER.warning("Analysis already in progress")
            return
        
        self.is_analyzing = True
        
        def on_result(results):
            self.current_analysis = results
            self.is_analyzing = False
            self.update_display(results)
        
        def on_progress(value):
            # Update progress bar in UI
            LOGGER.debug(f"Update progress bar: {value}%")
        
        def on_status(status):
            # Update status label in UI
            LOGGER.debug(f"Status: {status}")
        
        # Start async analysis
        worker = run_async(
            analyze_text_heavy,
            text,
            None,
            None,
            on_result=on_result,
            on_progress=on_progress
        )
        
        # Connect status signal
        worker.signals.status.connect(on_status)
    
    def update_display(self, results: Dict[str, Any]):
        """Update the UI with analysis results."""
        LOGGER.info(f"Updating display with: {results}")
        # This would update actual UI elements