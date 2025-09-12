#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Simplified tests for the AI hook system that avoid Qt/async issues."""

import pytest
from unittest.mock import Mock, patch
from manuskript import settings


class TestHookSystemSimple:
    """Test the basic hook system functionality without async complications."""
    
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
        
        # Enable AI features for testing
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
    
    def test_hook_registration_basic(self):
        """Test basic hook registration without triggering."""
        callback = Mock()
        
        settings.register_hook("text_changed", callback)
        
        assert len(settings.ai_hooks["text_changed"]) == 1
        assert settings.ai_hooks["text_changed"][0]["callback"] == callback
        assert settings.ai_hooks["text_changed"][0]["feature_key"] is None
    
    def test_hook_registration_with_feature(self):
        """Test hook registration with feature key."""
        callback = Mock()
        
        settings.register_hook("text_changed", callback, feature_key="narrativeGraphMemory")
        
        hook_entry = settings.ai_hooks["text_changed"][0]
        assert hook_entry["callback"] == callback
        assert hook_entry["feature_key"] == "narrativeGraphMemory"
    
    def test_hook_registration_priority_ordering(self):
        """Test that hooks are ordered by priority."""
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
    
    def test_hook_registration_invalid_event(self):
        """Test that registering invalid event raises error."""
        callback = Mock()
        
        with pytest.raises(ValueError, match="Invalid event"):
            settings.register_hook("invalid_event", callback)
    
    @patch('manuskript.settings._run_callback_async')
    def test_trigger_hook_basic_sync(self, mock_async):
        """Test basic synchronous hook triggering."""
        callback = Mock()
        callback._cpu_heavy = False  # Mark as not CPU-heavy
        settings.register_hook("text_changed", callback)
        
        # Mock to prevent async execution
        mock_async.return_value = True
        
        result = settings.trigger_hook("text_changed", "test text")
        
        assert result is True
        callback.assert_called_once_with("test text")
    
    def test_trigger_hook_feature_filtering(self):
        """Test that hooks are filtered by feature availability."""
        callback_enabled = Mock()
        callback_disabled = Mock()
        callback_no_feature = Mock()
        
        # Mark all as not CPU-heavy to avoid async complications
        for cb in [callback_enabled, callback_disabled, callback_no_feature]:
            cb._cpu_heavy = False
        
        settings.register_hook("text_changed", callback_enabled, feature_key="narrativeGraphMemory")
        settings.register_hook("text_changed", callback_disabled, feature_key="disabledFeature")
        settings.register_hook("text_changed", callback_no_feature)
        
        # Disable one feature
        settings.aiFeatures["disabledFeature"] = False
        
        result = settings.trigger_hook("text_changed", "test text")
        
        assert result is True
        callback_enabled.assert_called_once_with("test text")
        callback_disabled.assert_not_called()  # Feature disabled
        callback_no_feature.assert_called_once_with("test text")  # No feature requirement
    
    def test_trigger_hook_exception_handling(self):
        """Test that exceptions in hooks are handled gracefully."""
        callback_error = Mock(side_effect=Exception("Test error"))
        callback_normal = Mock()
        
        # Mark as not CPU-heavy
        callback_error._cpu_heavy = False
        callback_normal._cpu_heavy = False
        
        settings.register_hook("text_changed", callback_error)
        settings.register_hook("text_changed", callback_normal)
        
        # Should not raise exception but should return False due to error
        result = settings.trigger_hook("text_changed", "test text")
        
        assert result is False  # Should be False due to exception
        callback_error.assert_called_once()
        callback_normal.assert_called_once()  # Should still execute
    
    def test_hook_unregistration(self):
        """Test hook unregistration."""
        callback1 = Mock()
        callback2 = Mock()
        
        settings.register_hook("text_changed", callback1)
        settings.register_hook("text_changed", callback2)
        
        assert len(settings.ai_hooks["text_changed"]) == 2
        
        # Unregister one callback
        settings.unregister_hook("text_changed", callback1)
        
        assert len(settings.ai_hooks["text_changed"]) == 1
        assert settings.ai_hooks["text_changed"][0]["callback"] == callback2
    
    def test_multiple_event_types(self):
        """Test registration and triggering of different event types."""
        callbacks = {}
        for event_type in ["before_load", "after_load", "text_changed"]:
            callbacks[event_type] = Mock()
            callbacks[event_type]._cpu_heavy = False
            settings.register_hook(event_type, callbacks[event_type])
        
        # Trigger each event type
        settings.trigger_hook("before_load", "/test/path", Mock())
        settings.trigger_hook("after_load", "/test/path", Mock())  
        settings.trigger_hook("text_changed", "test text")
        
        # Verify each was called
        for callback in callbacks.values():
            callback.assert_called_once()
    
    def test_hook_system_state_isolation(self):
        """Test that different hook events don't interfere."""
        text_callback = Mock()
        character_callback = Mock()
        
        text_callback._cpu_heavy = False
        character_callback._cpu_heavy = False
        
        settings.register_hook("text_changed", text_callback)
        settings.register_hook("character_changed", character_callback)
        
        # Trigger only text_changed
        settings.trigger_hook("text_changed", "text data")
        
        text_callback.assert_called_once_with("text data")
        character_callback.assert_not_called()
        
        # Now trigger character_changed
        settings.trigger_hook("character_changed", "character data")
        
        character_callback.assert_called_once_with("character data")
        # text_callback should still only have been called once
        assert text_callback.call_count == 1


class TestHookSystemEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test environment."""
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def teardown_method(self):
        """Clean up."""
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
    
    def test_trigger_unknown_event(self):
        """Test triggering unknown event type."""
        result = settings.trigger_hook("unknown_event", "data")
        assert result is False
    
    def test_register_non_callable(self):
        """Test registering non-callable as callback."""
        with pytest.raises(ValueError, match="Callback must be callable"):
            settings.register_hook("text_changed", "not_callable")
    
    def test_empty_hook_list_trigger(self):
        """Test triggering event with no registered hooks."""
        result = settings.trigger_hook("text_changed", "data")
        assert result is True  # Should succeed with no hooks
    
    def test_feature_toggle_runtime(self):
        """Test toggling features at runtime."""
        callback = Mock()
        callback._cpu_heavy = False
        
        settings.register_hook("text_changed", callback, feature_key="narrativeGraphMemory")
        
        # Feature enabled - should call
        settings.aiFeatures["narrativeGraphMemory"] = True
        settings.trigger_hook("text_changed", "test1")
        callback.assert_called_once_with("test1")
        
        # Disable feature - should not call
        callback.reset_mock()
        settings.aiFeatures["narrativeGraphMemory"] = False
        settings.trigger_hook("text_changed", "test2")
        callback.assert_not_called()
        
        # Re-enable - should call again
        settings.aiFeatures["narrativeGraphMemory"] = True
        settings.trigger_hook("text_changed", "test3")
        callback.assert_called_once_with("test3")


class TestHookSystemPerformance:
    """Test hook system performance characteristics."""
    
    def setup_method(self):
        """Set up performance test environment."""
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
        settings.aiFeatures = {"narrativeGraphMemory": True}
    
    def teardown_method(self):
        """Clean up."""
        settings.ai_hooks = {
            "before_load": [],
            "after_load": [],
            "before_save": [],
            "text_changed": [],
            "character_changed": []
        }
    
    def test_many_hooks_registration(self):
        """Test registering many hooks performs reasonably."""
        import time
        
        start_time = time.time()
        
        # Register 1000 hooks
        for i in range(1000):
            callback = Mock()
            callback._cpu_heavy = False
            settings.register_hook("text_changed", callback, priority=i)
        
        registration_time = time.time() - start_time
        
        # Should complete registration quickly
        assert registration_time < 1.0, f"Registration took {registration_time}s, too slow"
        
        # Verify correct count and ordering
        assert len(settings.ai_hooks["text_changed"]) == 1000
        
        # Check priority ordering (first should have priority 0, last should have 999)
        assert settings.ai_hooks["text_changed"][0]["priority"] == 0
        assert settings.ai_hooks["text_changed"][-1]["priority"] == 999
    
    def test_many_hooks_triggering(self):
        """Test triggering many hooks performs reasonably."""
        import time
        
        # Register 100 simple hooks
        for i in range(100):
            callback = Mock()
            callback._cpu_heavy = False
            settings.register_hook("text_changed", callback)
        
        start_time = time.time()
        
        # Trigger hooks multiple times
        for _ in range(10):
            settings.trigger_hook("text_changed", "test data")
        
        trigger_time = time.time() - start_time
        
        # Should complete triggering quickly
        assert trigger_time < 1.0, f"Triggering took {trigger_time}s, too slow"
        
        # Verify all hooks were called correctly
        for hook in settings.ai_hooks["text_changed"]:
            callback = hook["callback"]
            assert callback.call_count == 10