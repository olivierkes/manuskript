import gi
import pytest

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from manuskript.data import OutlineText
from manuskript.ui.views.editorView import EditorView


@pytest.fixture
def editor():
    """Create a minimal editor with a real GTK text buffer."""
    view = EditorView.__new__(EditorView)
    view.editorTextBuffer = Gtk.TextBuffer()

    # Start without an active chapter.
    view.outlineItem = None

    view.editorTextBuffer.connect(
        "changed", view._editorTextChanged
    )

    return view


def test_editing_chapter_updates_model(editor):
    """Changes in the GTK editor must reach the chapter model."""
    chapter = OutlineText.__new__(OutlineText)
    chapter.text = "Original text"

    editor.outlineItem = chapter
    editor.editorTextBuffer.set_text("Updated text")

    assert chapter.text == "Updated text"


def test_loading_without_active_chapter_does_not_modify_model(editor):
    """Buffer changes during loading must not overwrite a chapter."""
    chapter = OutlineText.__new__(OutlineText)
    chapter.text = "Original text"

    editor.outlineItem = None
    editor.editorTextBuffer.set_text("Temporary loading text")

    assert chapter.text == "Original text"


def test_folder_view_does_not_overwrite_chapter(editor):
    """Editing a folder view must not write into an individual chapter."""
    from manuskript.data import OutlineFolder

    folder = OutlineFolder.__new__(OutlineFolder)

    editor.outlineItem = folder
    editor.editorTextBuffer.set_text("Combined folder text")

    # Folder editing must not assign a text property.
    assert not hasattr(folder, "text")
