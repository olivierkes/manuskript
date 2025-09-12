#!/usr/bin/env python
# --!-- coding: utf8 --!--
"""
Async Worker Module for AI Features

Provides QThreadPool-based async execution for CPU-heavy AI tasks
to prevent blocking the UI thread.
"""

from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, pyqtSlot
from manuskript import settings
import logging
import traceback
from typing import Callable, Any, Dict, Optional

LOGGER = logging.getLogger(__name__)

# Global thread pool for AI tasks
ai_thread_pool = None

def get_ai_thread_pool():
    """Get or create the global AI thread pool."""
    global ai_thread_pool
    if ai_thread_pool is None:
        ai_thread_pool = QThreadPool()
        # Limit threads to avoid overwhelming the system
        ai_thread_pool.setMaxThreadCount(2)
        LOGGER.info(f"Created AI thread pool with {ai_thread_pool.maxThreadCount()} threads")
    return ai_thread_pool

class WorkerSignals(QObject):
    """
    Signals for the AI worker to communicate with the main thread.
    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)

class AIWorker(QRunnable):
    """
    Worker thread for running AI tasks asynchronously.
    
    Inherits from QRunnable to handle worker thread setup and signals.
    """
    
    def __init__(self, fn: Callable, *args, **kwargs):
        """
        Initialize the worker.
        
        Args:
            fn: The function to run in the background
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
        # Add a callback to kwargs if needed
        self.kwargs['_worker_signals'] = self.signals
        
    @pyqtSlot()
    def run(self):
        """
        Execute the function in a background thread.
        """
        try:
            # Run the function
            result = self.fn(*self.args, **self.kwargs)
            
            # Emit result
            self.signals.result.emit(result)
            
        except Exception as e:
            # Emit error with exception info
            exctype, value = type(e), e
            tb = traceback.format_exc()
            self.signals.error.emit((exctype, value, tb))
            LOGGER.error(f"AI Worker error: {tb}")
            
        finally:
            self.signals.finished.emit()

def run_async(fn: Callable, *args, 
              on_result: Optional[Callable] = None,
              on_error: Optional[Callable] = None,
              on_finished: Optional[Callable] = None,
              on_progress: Optional[Callable] = None,
              **kwargs) -> AIWorker:
    """
    Run a function asynchronously in the AI thread pool.
    
    Args:
        fn: The function to run
        on_result: Callback for successful completion (receives result)
        on_error: Callback for errors (receives exception info)
        on_finished: Callback when task completes (regardless of success)
        on_progress: Callback for progress updates (receives int 0-100)
        *args: Positional arguments for fn
        **kwargs: Keyword arguments for fn
        
    Returns:
        AIWorker: The worker instance (for cancellation if needed)
    """
    worker = AIWorker(fn, *args, **kwargs)
    
    # Connect callbacks
    if on_result:
        worker.signals.result.connect(on_result)
    if on_error:
        worker.signals.error.connect(on_error)
    if on_finished:
        worker.signals.finished.connect(on_finished)
    if on_progress:
        worker.signals.progress.connect(on_progress)
    
    # Start the worker
    get_ai_thread_pool().start(worker)
    
    return worker

def trigger_hook_async(event: str, *args, **kwargs):
    """
    Trigger hooks asynchronously to avoid blocking the UI.
    
    This is a drop-in replacement for trigger_hook() that runs
    callbacks in background threads.
    
    Args:
        event: The hook event name
        *args: Positional arguments to pass to callbacks
        **kwargs: Keyword arguments to pass to callbacks
    """
    if event not in settings.ai_hooks:
        LOGGER.warning(f"Unknown hook event: {event}")
        return
    
    def run_hooks():
        """Inner function to run in thread."""
        for hook in settings.ai_hooks[event]:
            callback = hook["callback"]
            feature_key = hook.get("feature_key")
            
            try:
                # Only run if no feature_key is set, or if the feature is enabled
                if feature_key is None or settings.aiFeatures.get(feature_key, False):
                    # Check if callback has _worker_signals for progress reporting
                    if '_worker_signals' in kwargs:
                        # Pass signals to callback for progress updates
                        callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                        
            except Exception as e:
                callback_name = getattr(callback, "__name__", str(callback))
                LOGGER.error(f"[AI Hook Error] {event} callback {callback_name} failed: {e}")
    
    # Run hooks in background thread
    run_async(
        run_hooks,
        on_error=lambda err: LOGGER.error(f"Async hook execution failed: {err[2]}")
    )

class AsyncHookDecorator:
    """
    Decorator to mark functions as async-capable for the hook system.
    """
    
    def __init__(self, cpu_heavy: bool = False):
        """
        Args:
            cpu_heavy: If True, always run this hook in background thread
        """
        self.cpu_heavy = cpu_heavy
    
    def __call__(self, fn: Callable) -> Callable:
        """Wrap the function with async metadata."""
        fn._async_capable = True
        fn._cpu_heavy = self.cpu_heavy
        return fn

# Convenience decorator
async_hook = AsyncHookDecorator

def register_async_hook(event: str, callback: Callable, 
                        feature_key: Optional[str] = None,
                        priority: int = 10,
                        cpu_heavy: bool = False):
    """
    Register an async-capable hook.
    
    Args:
        event: The hook event name
        callback: The function to call
        feature_key: Optional AI feature key
        priority: Execution priority
        cpu_heavy: If True, always run in background thread
    """
    # Mark callback as async-capable
    callback._async_capable = True
    callback._cpu_heavy = cpu_heavy
    
    # Register normally
    settings.register_hook(event, callback, feature_key, priority)

def cleanup_thread_pool():
    """
    Clean up the thread pool on application shutdown.
    Should be called when the application exits.
    """
    global ai_thread_pool
    if ai_thread_pool:
        LOGGER.info("Waiting for AI threads to complete...")
        ai_thread_pool.waitForDone(5000)  # Wait max 5 seconds
        ai_thread_pool = None