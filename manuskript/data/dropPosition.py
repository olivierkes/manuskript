from enum import Enum, unique, auto
from gi.repository import Gtk


@unique
class DropPosition(Enum):
    NONE = auto()
    BEFORE = auto()
    AFTER = auto()
    INTO_OR_BEFORE = auto()
    INTO_OR_AFTER = auto()

    @classmethod
    def fromGtkEnum(cls, dropPosition: Gtk.TreeViewDropPosition):
        switch = {
            Gtk.TreeViewDropPosition.AFTER: DropPosition.AFTER,
            Gtk.TreeViewDropPosition.BEFORE: DropPosition.BEFORE,
            Gtk.TreeViewDropPosition.INTO_OR_AFTER: DropPosition.INTO_OR_AFTER,
            Gtk.TreeViewDropPosition.INTO_OR_BEFORE: DropPosition.INTO_OR_BEFORE,
            None: DropPosition.NONE
        }

        return switch.get(dropPosition, DropPosition.NONE)


