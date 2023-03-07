#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QSize, QModelIndex, Qt
from PyQt5.QtGui import QPixmap, QColor, QIcon, QBrush
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QColorDialog, QDialog

from manuskript.enums import Character
from manuskript.functions import iconColor, mainWindow
from manuskript.ui import style as S
from manuskript.ui import characterInfoDialog


class characterTreeView(QTreeWidget):
    """
    A QTreeWidget that displays characters from a characterModel in respect of their importance.
    """
    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self._model = None
        self._catRow = [-1, -1, -1]
        self._filter = ""
        self._lastID = -1
        self._updating = False
        self.setRootIsDecorated(False)
        self.setIndentation(10)
        self.setHeaderHidden(True)
        self.setIconSize(QSize(24, 24))

        self.setColumnCount(1)
        self._rootItem = QTreeWidgetItem()
        self.insertTopLevelItem(0, self._rootItem)

        self.importanceMap = {self.tr("Main"):2, self.tr("Secondary"):1, self.tr("Minor"):0}

    def setCharactersModel(self, model):
        self._model = model
        self._model.dataChanged.connect(self.updateMaybe)
        self._model.rowsInserted.connect(self.updateMaybe2)
        self._model.rowsRemoved.connect(self.updateMaybe2)
        self.updateItems()

    def setFilter(self, text):
        self._filter = text
        self.updateItems()

    def updateMaybe(self, topLeft, bottomRight):
        if topLeft.parent() != QModelIndex():
            return

        if topLeft.column() <= Character.name <= bottomRight.column():
            # Update name
            self.updateNames()

        elif topLeft.column() <= Character.importance <= bottomRight.column():
            # Importance changed
            self.updateItems()

    def updateMaybe2(self, parent, first, last):
        # Rows inserted or removed, we update only if they are topLevel rows.
        if parent == QModelIndex():
            self.updateItems()

    def updateNames(self):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)

            for child in range(item.childCount()):
                sub = item.child(child)
                ID = sub.data(0, Qt.UserRole)
                if ID != None:
                    # Update name
                    c = self._model.getCharacterByID(ID)
                    name = c.name()
                    sub.setText(0, name)
                    # Update icon
                    px = QPixmap(32, 32)
                    color = c.color()
                    px.fill(color)
                    sub.setIcon(0, QIcon(px))

    def updateItems(self):
        if not self._model:
            return

        if self.currentItem():
            self._lastID = self.currentItem().data(0, Qt.UserRole)

        self._updating = True
        self.clear()
        characters = self._model.getCharactersByImportance()

        for i, importanceLevel in enumerate(self.importanceMap):
            # Create category item
            cat = QTreeWidgetItem(self, [importanceLevel])
            cat.setBackground(0, QBrush(QColor(S.highlightLight)))
            cat.setForeground(0, QBrush(QColor(S.highlightedTextDark)))
            cat.setTextAlignment(0, Qt.AlignCenter)
            f = cat.font(0)
            f.setBold(True)
            cat.setFont(0, f)
            self.addTopLevelItem(cat)
            # cat.setChildIndicatorPolicy(cat.DontShowIndicator)

            for c in characters[i]:
                name = c.name()
                # Check if name passes filter
                if not self._filter.lower() in name.lower():
                    continue

                item = QTreeWidgetItem(cat, [name])
                item.setData(0, Qt.UserRole, c.ID())
                px = QPixmap(32, 32)
                color = QColor(c.color())
                px.fill(color)
                item.setIcon(0, QIcon(px))

                if c.ID() == self._lastID:
                    self.setCurrentItem(item)

        self.expandAll()
        self._updating = False

    def addCharacter(self):
        curr_item = self.currentItem()
        curr_importance = 0

        # check if an item is selected
        if curr_item != None:
            if curr_item.parent() == None:
                # this is a top-level category, so find its importance
                # get the current text, then look up the importance level
                text = curr_item.text(0)
                curr_importance = self.importanceMap[text]
            else:
                # get the importance from the currently-highlighted character
                curr_character = self.currentCharacter()
                curr_importance = curr_character.importance()

        self._model.addCharacter(importance=curr_importance)

    def removeCharacter(self):
        """
        Removes selected character.
        """
        ID = self.currentCharacterID()
        if ID is None:
            return None
        self._model.removeCharacter(ID)
        return ID

    def choseCharacterColor(self):
        ID = self.currentCharacterID()
        c = self._model.getCharacterByID(ID)

        if c:
            color = iconColor(c.icon)
        else:
            color = Qt.white

        self.colorDialog = QColorDialog(color, mainWindow())
        color = self.colorDialog.getColor(color)

        if color.isValid():
            c.setColor(color)
            mainWindow().updateCharacterColor(ID)

    def changeCharacterPOVState(self, state):
        ID = self.currentCharacterID()
        c = self._model.getCharacterByID(ID)
        c.setPOVEnabled(state == Qt.Checked)
        mainWindow().updateCharacterPOVState(ID)

    def addCharacterInfo(self):
        #Setting up dialog
        charInfoDialog = QDialog()
        charInfoUi = characterInfoDialog.Ui_characterInfoDialog()
        charInfoUi.setupUi(charInfoDialog)

        if charInfoDialog.exec_() == QDialog.Accepted:
            # User clicked OK, get the input values
            description = charInfoUi.descriptionLineEdit.text()
            value = charInfoUi.valueLineEdit.text()

            # Add the character info with the input values
            ID = self.currentCharacterID()
            self._model.addCharacterInfo(ID, description, value)



    def removeCharacterInfo(self):
        self._model.removeCharacterInfo(self.currentCharacterID())

    def currentCharacterID(self):
        ID = None
        if self.currentItem():
            ID = self.currentItem().data(0, Qt.UserRole)

        return ID

    def currentCharacterIDs(self): #Exactly like currentCharacterID(), except for multiselection
        IDs = []
        for item in self.selectedItems():
            ID = item.data(0, Qt.UserRole)
            if ID is not None:
                IDs.append(ID)
        return IDs

    def currentCharacter(self):
        """
        Returns the selected character
        @return: Character
        """
        ID = self.currentCharacterID()
        return self._model.getCharacterByID(ID)
    def currentCharacters(self):
        """
        Returns the selected characters (when multiple are selected)
        @return: List of Characters
        """
        IDs = self.currentCharacterIDs()
        characters = []
        for ID in IDs:
            characters.append(self._model.getCharacterByID(ID))
        return characters

    def getItemByID(self, ID):
        for t in range(self.topLevelItemCount()):
            for i in range(self.topLevelItem(t).childCount()):
                item = self.topLevelItem(t).child(i)
                if item.data(0, Qt.UserRole) == ID:
                    return item

    def mouseDoubleClickEvent(self, event):
        item = self.currentItem()
        if item is None:
            return
        # Catching double clicks to forbid collapsing of toplevel items
        if item.parent():
            QTreeWidget.mouseDoubleClickEvent(self, event)
