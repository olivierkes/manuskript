#!/usr/bin/env python
# --!-- coding: utf8 --!--
from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel, QVariant
from PyQt5.QtGui import QIcon, QPixmap, QColor

from manuskript.functions import randomColor, iconColor, mainWindow, search
from manuskript.enums import Character as C, Model
from manuskript.searchLabels import CharacterSearchLabels

from manuskript.models.searchableModel import searchableModel
from manuskript.models.searchableItem import searchableItem


class characterModel(QAbstractItemModel, searchableModel):

    def __init__(self, parent):
        QAbstractItemModel.__init__(self, parent)

        # CharacterItems are stored in this list
        self.characters = []

###############################################################################
# QAbstractItemModel subclassed
###############################################################################

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            c = parent.internalPointer()
            return len(c.infos)
        else:
            return len(self.characters)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            # Returns characters infos
            return 2
        else:
            return len(C)

    def data(self, index, role=Qt.DisplayRole):
        c = index.internalPointer()
        if type(c) == Character:
            if role == Qt.DisplayRole:
                if index.column() in c._data:
                    return c._data[index.column()]
                else:
                    return ""

            elif role == Qt.DecorationRole:
                if index.column() == C.name.value:
                    return c.icon
                else:
                    return QVariant()

        elif type(c) == CharacterInfo:
            if role == Qt.DisplayRole or role == Qt.EditRole:
                if index.column() == 0:
                    return c.description
                elif index.column() == 1:
                    return c.value

    def setData(self, index, value, role=Qt.EditRole):
        c = index.internalPointer()
        if type(c) == Character:
            if role == Qt.EditRole:
                # We update only if data is different
                if index.column() not in c._data or c._data[index.column()] != value:
                    c._data[index.column()] = value
                    self.dataChanged.emit(index, index)
                    return True

        elif type(c) == CharacterInfo:
            if role == Qt.EditRole:
                if index.column() == 0:
                    c.description = value
                elif index.column() == 1:
                    c.value = value
                self.dataChanged.emit(index, index)
                return True

        return False

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            return self.createIndex(row, column, self.characters[row])

        else:
            c = parent.internalPointer()
            if row < len(c.infos):
                return self.createIndex(row, column, c.infos[row])
            else:
                return QModelIndex()

    def indexFromItem(self, item, column=0):
        if not item:
            return QModelIndex()

        row = self.characters.index(item)
        col = column
        return self.createIndex(row, col, item)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child = index.internalPointer()

        if type(child) == Character:
            return QModelIndex()

        elif type(child) == CharacterInfo:
            return child.character.index()

    def flags(self, index):
        if index.parent().isValid():
            return QAbstractItemModel.flags(self, index) | Qt.ItemIsEditable
        else:
            return QAbstractItemModel.flags(self, index)

###############################################################################
# CHARACTER QUERIES
###############################################################################

    def character(self, row):
        return self.characters[row]

    def name(self, row):
        return self.character(row).name()

    def icon(self, row):
        return self.character(row).icon

    def ID(self, row):
        return self.character(row).ID()

    def importance(self, row):
        return self.character(row).importance()

    def pov(self, row):
        return self.character(row).pov()

###############################################################################
# MODEL QUERIES
###############################################################################

    def getCharactersByImportance(self):
        """
        Lists characters by importance.

        @return: array of array of ´character´, by importance.
        """
        r = [[], [], []]

        for c in self.characters:
            r[2-int(c.importance())].append(c)

        return r

    def getCharacterByID(self, ID):
        if ID != None:
            ID = str(ID)
            for c in self.characters:
                if c.ID() == ID:
                    return c

        return None

###############################################################################
# ADDING / REMOVING
###############################################################################

    def addCharacter(self, importance=0, name=None):
        """
        Creates a new character
        @param importance: the importance level of the character
        @return: the character
        """
        if not name:
            name = self.tr("New character")

        c = Character(model=self, name=self.tr(name), importance=importance)
        self.beginInsertRows(QModelIndex(), len(self.characters), len(self.characters))
        self.characters.append(c)
        self.endInsertRows()
        return c

    def removeCharacter(self, ID):
        """
        Removes character whose ID is ID...
        @param ID: the ID of the character to remove
        @return: nothing
        """
        c = self.getCharacterByID(ID)
        self.beginRemoveRows(QModelIndex(), self.characters.index(
            c), self.characters.index(c))
        self.characters.remove(c)
        self.endRemoveRows()

###############################################################################
# CHARACTER INFOS
###############################################################################

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return self.tr("Name")
            elif section == 1:
                return self.tr("Value")
            else:
                return C(section).name

    def addCharacterInfo(self, ID):
        c = self.getCharacterByID(ID)
        self.beginInsertRows(c.index(), len(c.infos), len(c.infos))
        c.infos.append(CharacterInfo(
            c,
            description=self.tr("Description"),
            value=self.tr("Value")
        ))
        self.endInsertRows()

        mainWindow().updatePersoInfoView()

    def removeCharacterInfo(self, ID):
        c = self.getCharacterByID(ID)

        rm = []
        for idx in mainWindow().tblPersoInfos.selectedIndexes():
            if not idx.row() in rm:
                rm.append(idx.row())

        rm.sort()
        rm.reverse()
        for r in rm:
            self.beginRemoveRows(c.index(), r, r)
            c.infos.pop(r)
            self.endRemoveRows()

    def searchableItems(self):
        return self.characters

###############################################################################
# CHARACTER
###############################################################################


class Character(searchableItem):

    def __init__(self, model, name=None, importance=0):
        self._model = model
        self.lastPath = ""

        if not name:
            name = self.translate("Unknown")

        self._data = {C.name.value: name}
        self.assignUniqueID()
        self.assignRandomColor()
        self._data[C.importance.value] = str(importance)
        self._data[C.pov.value] = "True"

        self.infos = []

        super().__init__(CharacterSearchLabels)

    def name(self):
        return self._data[C.name.value]

    def setName(self, value):
        self._data[C.name.value] = value

    def importance(self):
        return self._data[C.importance.value]

    def ID(self):
        return self._data[C.ID.value]

    def index(self, column=0):
        return self._model.indexFromItem(self, column)

    def data(self, column, role=Qt.DisplayRole):
        if column == "Info":
            return self.infos
        else:
            return self._data.get(column, role)

    def assignRandomColor(self):
        """
        Assigns a random color the the character.
        """
        color = randomColor(QColor(Qt.white))
        self.setColor(color)

    def setColor(self, color):
        """
        Sets the character's color
        @param color: QColor.
        """
        px = QPixmap(32, 32)
        px.fill(color)
        self.icon = QIcon(px)
        try:
            self._model.dataChanged.emit(self.index(), self.index())
        except:
            # If it is the initialisation, won't be able to emit
            pass

    def color(self):
        """
        Returns character's color in QColor
        @return: QColor
        """
        return iconColor(self.icon)

    def setPOVEnabled(self, enabled):
        if enabled != self.pov():
            if enabled:
                self._data[C.pov.value] = 'True'
            else:
                self._data[C.pov.value] = 'False'

            try:
                self._model.dataChanged.emit(self.index(), self.index())
            except:
                # If it is the initialisation, won't be able to emit
                pass

    def pov(self):
        return self._data[C.pov.value] == 'True'

    def assignUniqueID(self, parent=QModelIndex()):
        """Assigns an unused character ID."""
        vals = []
        for c in self._model.characters:
            vals.append(int(c.ID()))

        k = 0
        while k in vals:
            k += 1

        self._data[C.ID.value] = str(k)

    def listInfos(self):
        r = []
        for i in self.infos:
            r.append((i.description, i.value))
        return r

    def searchTitle(self, column):
        return self.name()

    def searchOccurrences(self, searchRegex, column):
        results = []

        data = self.searchData(column)
        if isinstance(data, list):
            for i in range(0, len(data)):
                # For detailed info we will highlight the full row, so we pass the row index
                # to the highlighter instead of the (startPos, endPos) of the match itself.
                results += [self.wrapSearchOccurrence(column, i, 0, context) for
                            (startPos, endPos, context) in search(searchRegex, data[i].description)]
                results += [self.wrapSearchOccurrence(column, i, 0, context) for
                            (startPos, endPos, context) in search(searchRegex, data[i].value)]
        else:
            results += super().searchOccurrences(searchRegex, column)

        return results

    def searchID(self):
        return self.ID()

    def searchPath(self, column):
        return [self.translate("Characters"), self.name(), self.translate(self.searchColumnLabel(column))]

    def searchData(self, column):
        if column == C.infos:
            return self.infos
        else:
            return self.data(column)

    def searchModel(self):
        return Model.Character


class CharacterInfo():
    def __init__(self, character, description="", value=""):
        self.description = description
        self.value = value
        self.character = character
