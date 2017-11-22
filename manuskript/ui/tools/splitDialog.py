#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtWidgets import QInputDialog
from manuskript.functions import mainWindow


class splitDialog(QInputDialog):
    """
    Opens a dialog to split indexes.
    """
    def __init__(self, parent, indexes, mark=None):
        """
        @param parent:  a QWidget, for the dialog.
        @param indexes: a list of QModelIndex in the outlineModel
        @param default: the default split mark
        """
        QInputDialog.__init__(self, parent)

        description = self.tr("""
            <p>Split selected item(s) at the given mark.</p>

            <p>If one of the selected item is a folder, it will be applied
            recursively to <i>all</i> of it's children items.</p>

            <p>The split mark can contain folling escape sequences:
                <ul>
                    <li><b><code>\\n</code></b>: line break</li>
                    <li><b><code>\\t</code></b>: tab</li>
                </ul>
            </p>

            <p><b>Mark:</b></p>
            """)

        if not mark:
            mark = "\\n---\\n"
        mark = mark.replace("\n", "\\n")
        mark = mark.replace("\t", "\\t")

        self.setLabelText(description)
        self.setTextValue(mark)

        if len(indexes) == 0:
            return
        if len(indexes) == 1:
            idx =  indexes[0]
            self.setWindowTitle(
                self.tr("Split '{}'").format(self.getItem(idx).title())
                )
        else:
            self.setWindowTitle(self.tr("Split items"))

        r = self.exec()

        mark = self.textValue()

        if r and mark:

            mark = mark.replace("\\n", "\n")
            mark = mark.replace("\\t", "\t")

            for idx in indexes:
                item = self.getItem(idx)
                item.split(mark)

    def getItem(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return mainWindow().mdlOutline.rootItem
