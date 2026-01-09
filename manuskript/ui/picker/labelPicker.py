from manuskript.data.labels import Label
from manuskript.ui.util import pixbufFromColor
from manuskript.ui.picker.abstractGridPicker import AbstractGridPicker
from gi.repository import GObject

class LabelPicker(AbstractGridPicker):
    __gsignals__ = {
        "label-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, labels):
        self.labels = labels

        super().__init__(enableSearch=True, columns=3)

        self.connect("item-selected", self._onLabelSelected)

    def show(self):
        super().show()

    def shouldIncludeItem(self, character):
        return True

    def getItems(self):
        return self.labels

    def getItemLabel(self, label: Label):
        return label.name

    def getItemPixbuf(self, label: Label):
        return pixbufFromColor(label.color)

    def getItemFilterKey(self, label: Label):
        return None

    def _onLabelSelected(self, picker, character):
        picker.emit("label-selected", character)