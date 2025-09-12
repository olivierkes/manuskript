# AI Features Module

This module provides AI-powered features for Manuskript through a flexible hook system.

## Hook System Overview

The hook system allows AI features to integrate seamlessly with Manuskript without modifying core functionality. Available hooks include:

### Core Hooks
- `before_save`: Triggered before a project is saved
- `after_save`: Triggered after a successful save
- `before_load`: Triggered before loading a project
- `after_load`: Triggered after loading a project
- `text_changed`: Triggered when text content changes
- `character_changed`: Triggered when character data changes
- `outline_changed`: Triggered when outline structure changes
- `plot_changed`: Triggered when plot elements change

## Creating New AI Modules

To create a new AI feature module:

1. Create a new Python file in the `ai/` directory
2. Define an `initialize()` function that registers your hooks
3. Import and initialize your module in `ai/__init__.py`

### Example Module Structure

```python
from manuskript import settings
import logging

LOGGER = logging.getLogger(__name__)

def initialize():
    """Initialize the module and register hooks."""
    settings.register_hook("text_changed", on_text_changed)
    settings.register_hook("after_save", on_save)
    
def on_text_changed(text, index, editor):
    """Handle text changes."""
    if not settings.aiFeatures.get("yourFeatureName", False):
        return
    
    # Your AI processing here
    pass

def on_save(project_path, main_window):
    """Handle project save."""
    if not settings.aiFeatures.get("yourFeatureName", False):
        return
    
    # Save your AI data
    pass
```

## Included Modules

### Narrative Graph Memory (`narrative_graph.py`)
Tracks story elements including:
- Character relationships and interactions
- Plot developments and continuity
- Setting details and consistency
- Narrative arcs and themes

### Adaptive Voice Style (`adaptive_voice.py`)
Learns and adapts to writing style:
- Analyzes sentence and paragraph structure
- Tracks vocabulary and word usage patterns
- Maintains character-specific voice profiles
- Provides style consistency suggestions

## Usage

The AI features are automatically initialized when Manuskript starts. To enable specific features:

1. Go to Settings > AI Features
2. Enter your Claude API key (if using AI-powered features)
3. Toggle individual features on/off

## Integration Points

To integrate AI features into your Manuskript workflow:

```python
# In your main application initialization
from manuskript.ai import initialize_ai_features

# Initialize all AI features
initialize_ai_features()
```

## Data Storage

AI modules store their data alongside project files:
- `.narrative_graph.json`: Narrative graph data
- `.style_profile.json`: Writing style patterns
- Additional module-specific files as needed

## Best Practices

1. **Check Feature Flags**: Always check if a feature is enabled before processing
2. **Handle Exceptions**: Wrap AI processing in try-except blocks to prevent crashes
3. **Optimize Performance**: Use the hook system efficiently to avoid slowing down the editor
4. **Respect Privacy**: Store AI data locally with the project, not in external services
5. **Provide Feedback**: Log important events for debugging and user feedback

## Extending the System

To add new hook points:

1. Add the hook name to `ai_hooks` dictionary in `settings.py`
2. Call `settings.trigger_hook()` at the appropriate location in the codebase
3. Document the hook parameters and usage

## Future Enhancements

Planned features and improvements:
- Real-time AI suggestions panel
- Advanced NLP for plot analysis
- Character dialogue generation
- Scene continuation suggestions
- Style mimicry for ghost writing
- Automated consistency checking
- Research assistant integration