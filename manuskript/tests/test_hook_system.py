#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for the AI hook system."""

import pytest
import tempfile
from unittest.mock import Mock, patch, MagicMock
from manuskript import settings


class TestHookSystem:
    """Test the feature-aware hook system."""
    
    def setup_method(self):
        """Set up test environment."""
        # Reset hook system state
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
        
        # Mock AI features as enabled for most tests
        self.original_ai_features = getattr(settings, 'aiFeatures', {})
        settings.aiFeatures = {
            "narrativeGraphMemory": True,
            "characterAnalysis": True
        }
    
    def teardown_method(self):
        """Clean up after tests."""
        settings.aiFeatures = self.original_ai_features
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
    
    def test_register_hook_basic(self):
        """Test basic hook registration."""
        callback = Mock()
        
        settings.register_hook("text_changed", callback)
        
        assert len(settings.ai_hooks["text_changed"]) == 1
        assert settings.ai_hooks["text_changed"][0]["callback"] == callback
        assert settings.ai_hooks["text_changed"][0]["feature_key"] is None
    
    def test_register_hook_with_feature_key(self):
        """Test hook registration with feature key."""
        callback = Mock()
        
        settings.register_hook("text_changed", callback, feature_key="narrativeGraphMemory")
        
        hook_entry = settings.ai_hooks["text_changed"][0]
        assert hook_entry["callback"] == callback
        assert hook_entry["feature_key"] == "narrativeGraphMemory"
    
    def test_register_hook_with_priority(self):
        """Test hook registration with priority ordering."""
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()
        
        settings.register_hook("text_changed", callback1, priority=20)
        settings.register_hook("text_changed", callback2, priority=5)
        settings.register_hook("text_changed", callback3, priority=15)
        
        # Should be ordered by priority: callback2(5), callback3(15), callback1(20)
        hooks = settings.ai_hooks["text_changed"]
        assert hooks[0]["callback"] == callback2
        assert hooks[1]["callback"] == callback3
        assert hooks[2]["callback"] == callback1
    
    def test_register_hook_invalid_event(self):
        """Test that registering invalid event raises error."""
        callback = Mock()
        
        with pytest.raises(ValueError, match="Invalid event"):
            settings.register_hook("invalid_event", callback)
    
    def test_trigger_hook_basic(self):
        """Test basic hook triggering."""
        callback = Mock()
        settings.register_hook("text_changed", callback)
        
        settings.trigger_hook("text_changed", "test text", index=None, editor=None)
        
        callback.assert_called_once_with("test text", index=None, editor=None)
    
    def test_trigger_hook_feature_enabled(self):
        """Test hook triggering when feature is enabled."""
        callback = Mock()
        settings.register_hook("text_changed", callback, feature_key="narrativeGraphMemory")
        
        settings.trigger_hook("text_changed", "test text")
        
        callback.assert_called_once_with("test text")
    
    def test_trigger_hook_feature_disabled(self):
        """Test hook not triggered when feature is disabled."""
        callback = Mock()
        settings.register_hook("text_changed", callback, feature_key="narrativeGraphMemory")
        
        # Disable the feature
        settings.aiFeatures["narrativeGraphMemory"] = False
        
        settings.trigger_hook("text_changed", "test text")
        
        callback.assert_not_called()
    
    def test_trigger_hook_mixed_features(self):
        """Test hooks with different feature requirements."""
        callback_enabled = Mock()
        callback_disabled = Mock()
        callback_no_feature = Mock()
        
        settings.register_hook("text_changed", callback_enabled, feature_key="narrativeGraphMemory")
        settings.register_hook("text_changed", callback_disabled, feature_key="disabledFeature")
        settings.register_hook("text_changed", callback_no_feature)
        
        settings.aiFeatures["disabledFeature"] = False
        
        settings.trigger_hook("text_changed", "test text")
        
        callback_enabled.assert_called_once()
        callback_disabled.assert_not_called()
        callback_no_feature.assert_called_once()
    
    def test_trigger_hook_exception_handling(self):
        """Test that exceptions in hooks don't break the system."""
        callback_error = Mock(side_effect=Exception("Test error"))
        callback_normal = Mock()
        
        settings.register_hook("text_changed", callback_error)
        settings.register_hook("text_changed", callback_normal)
        
        # Should not raise exception
        settings.trigger_hook("text_changed", "test text")
        
        callback_error.assert_called_once()
        callback_normal.assert_called_once()
    
    def test_trigger_hook_async_decorator(self):
        """Test async hook triggering."""
        try:
            from manuskript.ai.async_worker import async_hook
        except ImportError:
            pytest.skip("Async worker not available")
        
        callback_calls = []
        
        @async_hook(cpu_heavy=True)
        def test_callback(text):
            callback_calls.append(text)
            return "processed"
        
        # Register and trigger
        settings.register_hook("text_changed", test_callback)
        settings.trigger_hook("text_changed", "test text")
        
        # Should have called the callback (may be async)
        # We just verify it has the async attributes
        assert hasattr(test_callback, '_cpu_heavy')
        assert test_callback._cpu_heavy is True
    
    def test_multiple_event_types(self):
        """Test that different event types work correctly."""
        before_load_callback = Mock()
        after_load_callback = Mock()
        text_changed_callback = Mock()
        
        settings.register_hook("before_load", before_load_callback)
        settings.register_hook("after_load", after_load_callback)
        settings.register_hook("text_changed", text_changed_callback)
        
        # Trigger different events
        settings.trigger_hook("before_load", "/path/to/project", mock_mainwindow=Mock())
        settings.trigger_hook("after_load", "/path/to/project", mock_mainwindow=Mock())
        settings.trigger_hook("text_changed", "some text")
        
        before_load_callback.assert_called_once()
        after_load_callback.assert_called_once()
        text_changed_callback.assert_called_once()
    
    def test_hook_system_isolation(self):
        """Test that hooks for different events don't interfere."""
        text_callback = Mock()
        character_callback = Mock()
        
        settings.register_hook("text_changed", text_callback)
        settings.register_hook("character_changed", character_callback)
        
        settings.trigger_hook("text_changed", "text")
        
        text_callback.assert_called_once()
        character_callback.assert_not_called()


class TestAsyncHookDecorator:
    """Test the async hook decorator functionality."""
    
    def test_async_hook_decorator(self):
        """Test that async hook decorator works correctly."""
        try:
            from manuskript.ai.async_worker import async_hook
        except ImportError:
            pytest.skip("Async worker not available")
        
        @async_hook(cpu_heavy=True)
        def test_function(arg1, arg2="default"):
            return f"processed {arg1} {arg2}"
        
        # The decorator should add attributes to the function
        assert hasattr(test_function, '_cpu_heavy')
        assert test_function._cpu_heavy is True
    
    def test_async_hook_decorator_preservation(self):
        """Test that async hook decorator preserves function metadata."""
        try:
            from manuskript.ai.async_worker import async_hook
        except ImportError:
            pytest.skip("Async worker not available")
        
        @async_hook(cpu_heavy=False)
        def test_function(arg1, arg2="default"):
            """Test function docstring."""
            return f"processed {arg1} {arg2}"
        
        assert test_function.__name__ == "test_function"
        assert "Test function docstring" in test_function.__doc__
        assert test_function._cpu_heavy is False