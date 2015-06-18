#!/usr/bin/env python
#--!-- coding: utf8 --!--

from qt import *

from ui.settings import *
from enums import *
from functions import *
import settings
import os

# Spell checker support
try:
    import enchant
except ImportError:
    enchant = None

class settingsWindow(QWidget, Ui_Settings):
    
    def __init__(self, mainWindow):
        QWidget.__init__(self)
        self.setupUi(self)
        self.mw = mainWindow
        
        # UI
        for i in range(self.lstMenu.count()):
            item = self.lstMenu.item(i)
            item.setSizeHint(QSize(item.sizeHint().width(), 42))
            item.setTextAlignment(Qt.AlignCenter)
        self.lstMenu.setMaximumWidth(150)
        
        # General
        self.cmbStyle.addItems(list(QStyleFactory.keys()))
        self.cmbStyle.setCurrentIndex([i.lower() for i in list(QStyleFactory.keys())].index(qApp.style().objectName()))
        self.cmbStyle.currentIndexChanged[str].connect(self.setStyle)
        
        self.txtAutoSave.setValidator(QIntValidator(0, 999, self))
        self.txtAutoSaveNoChanges.setValidator(QIntValidator(0, 999, self))
        self.chkAutoSave.setChecked(settings.autoSave)
        self.chkAutoSaveNoChanges.setChecked(settings.autoSaveNoChanges)
        self.txtAutoSave.setText(str(settings.autoSaveDelay))
        self.txtAutoSaveNoChanges.setText(str(settings.autoSaveNoChangesDelay))
        self.chkSaveOnQuit.setChecked(settings.saveOnQuit)
        self.chkAutoSave.stateChanged.connect(self.saveSettingsChanged)
        self.chkAutoSaveNoChanges.stateChanged.connect(self.saveSettingsChanged)
        self.chkSaveOnQuit.stateChanged.connect(self.saveSettingsChanged)
        self.txtAutoSave.textEdited.connect(self.saveSettingsChanged)
        self.txtAutoSaveNoChanges.textEdited.connect(self.saveSettingsChanged)
        
        # Views
        self.tabViews.setCurrentIndex(0)
        lst = ["Nothing", "POV", "Label", "Progress", "Compile"]
        for cmb in self.viewSettingsDatas():
            item, part = self.viewSettingsDatas()[cmb]
            cmb.setCurrentIndex(lst.index(settings.viewSettings[item][part]))
            cmb.currentIndexChanged.connect(self.viewSettingsChanged)
        
        for chk in self.outlineColumnsData():
            col = self.outlineColumnsData()[chk]
            chk.setChecked(col in settings.outlineViewColumns)
            chk.stateChanged.connect(self.outlineColumnsChanged)
            
        self.populatesCmbBackgrounds(self.cmbCorkImage)
        self.setCorkImageDefault()
        self.updateCorkColor()
        self.cmbCorkImage.currentIndexChanged.connect(self.setCorkBackground)
        self.btnCorkColor.clicked.connect(self.setCorkColor)
        
        # Labels
        self.lstLabels.setModel(self.mw.mdlLabels)
        self.lstLabels.setRowHidden(0, True)
        self.lstLabels.clicked.connect(self.updateLabelColor)
        self.btnLabelAdd.clicked.connect(self.addLabel)
        self.btnLabelRemove.clicked.connect(self.removeLabel)
        self.btnLabelColor.clicked.connect(self.setLabelColor)
        
        # Statuses
        self.lstStatus.setModel(self.mw.mdlStatus)
        self.lstStatus.setRowHidden(0, True)
        self.btnStatusAdd.clicked.connect(self.addStatus)
        self.btnStatusRemove.clicked.connect(self.removeStatus)
        
        # Fullscreen
        self._editingTheme = None
          # Preview editor
        self.previewText = QTextEdit()
        self.previewText.setFrameStyle(QFrame.NoFrame)
        self.previewText.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.previewText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.previewText.setPlainText(open(appPath("resources/themes/preview.txt")).read())
          # UI stuff
        self.btnThemeEditOK.setIcon(qApp.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.btnThemeEditOK.clicked.connect(self.saveTheme)
        self.btnThemeEditCancel.setIcon(qApp.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.btnThemeEditCancel.clicked.connect(self.cancelEdit)
        self.cmbThemeEdit.currentIndexChanged.connect(self.themeEditStack.setCurrentIndex)
        self.cmbThemeEdit.setCurrentIndex(0)
        self.cmbThemeEdit.currentIndexChanged.emit(0)
        self.themeStack.setCurrentIndex(0)
        self.populatesThemesList()
        self.lstThemes.currentItemChanged.connect(self.themeSelected)
        self.btnThemeAdd.clicked.connect(self.newTheme)
        self.btnThemeEdit.clicked.connect(self.editTheme)
        self.btnThemeRemove.clicked.connect(self.removeTheme)
        
        
    def setTab(self, tab):
        
        tabs = {
            "General":0,
            "Views":1,
            "Labels":2,
            "Status":3,
            "Fullscreen":4,
            }
        
        if tab in tabs:
            self.lstMenu.setCurrentRow(tabs[tab])
        else:
            self.lstMenu.setCurrentRow(tab)
####################################################################################################
#                                           GENERAL                                                #
####################################################################################################
        
    def setStyle(self, style):
        #Save style to Qt Settings
        settings = QSettings(qApp.organizationName(), qApp.applicationName())
        settings.setValue("applicationStyle", style)
        qApp.setStyle(style)
        
    def saveSettingsChanged(self):
        if self.txtAutoSave.text() in ["", "0"]:
            self.txtAutoSave.setText("1")
        if self.txtAutoSaveNoChanges.text() in ["", "0"]:
            self.txtAutoSaveNoChanges.setText("1")
        
        settings.autoSave = True if self.chkAutoSave.checkState() else False
        settings.autoSaveNoChanges = True if self.chkAutoSaveNoChanges.checkState() else False
        settings.saveOnQuit = True if self.chkSaveOnQuit.checkState() else False
        settings.autoSaveDelay = int(self.txtAutoSave.text())
        settings.autoSaveNoChangesDelay = int(self.txtAutoSaveNoChanges.text())
        self.mw.saveTimer.setInterval(settings.autoSaveDelay * 60 * 1000)
        self.mw.saveTimerNoChanges.setInterval(settings.autoSaveNoChangesDelay * 1000)

####################################################################################################
#                                           VIEWS                                                  #
####################################################################################################

    def viewSettingsDatas(self):
        return {
            self.cmbTreeIcon: ("Tree", "Icon"),
            self.cmbTreeText: ("Tree", "Text"),
            self.cmbTreeBackground: ("Tree", "Background"),
            self.cmbOutlineIcon: ("Outline", "Icon"),
            self.cmbOutlineText: ("Outline", "Text"),
            self.cmbOutlineBackground: ("Outline", "Background"),
            self.cmbCorkIcon: ("Cork", "Icon"),
            self.cmbCorkText: ("Cork", "Text"),
            self.cmbCorkBackground: ("Cork", "Background"),
            self.cmbCorkBorder: ("Cork", "Border"),
            self.cmbCorkCorner: ("Cork", "Corner")
            }
        
    def viewSettingsChanged(self):
        cmb = self.sender()
        lst = ["Nothing", "POV", "Label", "Progress", "Compile"]
        item, part = self.viewSettingsDatas()[cmb]
        element = lst[cmb.currentIndex()]
        self.mw.setViewSettings(item, part, element)
        
    def outlineColumnsData(self):
        return {
            self.chkOutlineTitle: Outline.title.value,
            self.chkOutlinePOV: Outline.POV.value,
            self.chkOutlineLabel: Outline.label.value,
            self.chkOutlineStatus: Outline.status.value,
            self.chkOutlineCompile: Outline.compile.value,
            self.chkOutlineWordCount: Outline.wordCount.value,
            self.chkOutlineGoal: Outline.goal.value,
            self.chkOutlinePercentage: Outline.goalPercentage.value,
            }
        
    def outlineColumnsChanged(self):
        chk = self.sender()
        val = True if chk.checkState() else False
        col = self.outlineColumnsData()[chk]
        if val and not col in settings.outlineViewColumns:
            settings.outlineViewColumns.append(col)
        elif not val and col in settings.outlineViewColumns:
            settings.outlineViewColumns.remove(col)
        
        # Update views
        self.mw.redacEditor.outlineView.hideColumns()
        self.mw.treePlanOutline.hideColumns()
        
    def setCorkColor(self):
        color = QColor(settings.corkBackground["color"])
        self.colorDialog = QColorDialog(color, self)
        color = self.colorDialog.getColor(color)
        if color.isValid():
            settings.corkBackground["color"] = color.name()
            self.updateCorkColor()
            # Update Cork view 
            self.mw.redacEditor.corkView.updateBackground()
        
    def updateCorkColor(self):
        self.btnCorkColor.setStyleSheet("background:{};".format(settings.corkBackground["color"]))
    
    def setCorkBackground(self, i):
        img = self.cmbCorkImage.itemData(i)
        if img:
            settings.corkBackground["image"] = img
        else:
            settings.corkBackground["image"] = ""
        # Update Cork view 
        self.mw.redacEditor.corkView.updateBackground()
    
    def populatesCmbBackgrounds(self, cmb):
        #self.cmbDelegate = cmbPixmapDelegate()
        #self.cmbCorkImage.setItemDelegate(self.cmbDelegate)
        
        paths = allPaths("resources/backgrounds")
        cmb.clear()
        cmb.addItem(QIcon.fromTheme("list-remove"), "", "")
        for p in paths:
            lst = os.listdir(p)
            for l in lst:
                if l.lower()[-4:] in [".jpg", ".png"] or \
                l.lower()[-5:] in [".jpeg"]:
                    px = QPixmap(os.path.join(p, l)).scaled(128, 64, Qt.KeepAspectRatio)
                    cmb.addItem(QIcon(px), "", os.path.join(p, l))
        
        cmb.setIconSize(QSize(128, 64))
        
    def setCorkImageDefault(self):
        if settings.corkBackground["image"] != "":
            i = self.cmbCorkImage.findData(settings.corkBackground["image"])
            if i != -1:
                self.cmbCorkImage.setCurrentIndex(i)

####################################################################################################
#                                           STATUS                                                 #
####################################################################################################

    def addStatus(self):
        self.mw.mdlStatus.appendRow(QStandardItem(self.tr("New status")))
        
    def removeStatus(self):
        for i in self.lstStatus.selectedIndexes():
            self.mw.mdlStatus.removeRows(i.row(), 1)
    
####################################################################################################
#                                           LABELS                                                 #
####################################################################################################
        
    def updateLabelColor(self, index):
        #px = QPixmap(64, 64)
        #px.fill(iconColor(self.mw.mdlLabels.item(index.row()).icon()))
        #self.btnLabelColor.setIcon(QIcon(px))
        self.btnLabelColor.setStyleSheet("background:{};".format(iconColor(self.mw.mdlLabels.item(index.row()).icon()).name()))
        self.btnLabelColor.setEnabled(True)
    
    def addLabel(self):
        px = QPixmap(32, 32)
        px.fill(Qt.transparent)
        self.mw.mdlLabels.appendRow(QStandardItem(QIcon(px), self.tr("New label")))
    
    def removeLabel(self):
        for i in self.lstLabels.selectedIndexes():
            self.mw.mdlLabels.removeRows(i.row(), 1)
            
    def setLabelColor(self):
        index = self.lstLabels.currentIndex()
        color = iconColor(self.mw.mdlLabels.item(index.row()).icon())
        self.colorDialog = QColorDialog(color, self)
        color = self.colorDialog.getColor(color)
        if color.isValid():
            px = QPixmap(32, 32)
            px.fill(color)
            self.mw.mdlLabels.item(index.row()).setIcon(QIcon(px))
            self.updateLabelColor(index)
    
####################################################################################################
#                                       FULLSCREEN                                                 #
####################################################################################################

    def themeSelected(self, current, previous):
        if current:
            self.btnThemeEdit.setEnabled(current.data(Qt.UserRole+1))
            self.btnThemeRemove.setEnabled(current.data(Qt.UserRole+1))
        else:
            self.btnThemeEdit.setEnabled(False)
            self.btnThemeRemove.setEnabled(False)
    
    def newTheme(self):
        path = writablePath("resources/themes")
        name = self.tr("newtheme")
        if os.path.exists(os.path.join(path, "{}.theme".format(name))):
            i = 1
            while os.path.exists(os.path.join(path, "{}_{}.theme".format(name, i))):
                i += 1
            name = os.path.join(path, "{}_{}.theme".format(name, i))
        else:
            name = os.path.join(path, "{}.theme".format(name))
        
        settings = QSettings(name, QSettings.IniFormat)
        settings.setValue("Name", self.tr("New theme"))
        settings.sync()
        print(name)
        
        self.populatesThemesList()
        
    def editTheme(self):
        item = self.lstThemes.currentItem()
        theme = item.data(Qt.UserRole)
        self.loadTheme(theme)
        self.themeStack.setCurrentIndex(1)
    
    def removeTheme(self):
        item = self.lstThemes.currentItem()
        theme = item.data(Qt.UserRole)
        os.remove(theme)
        self.populatesThemesList()
    
    def populatesThemesList(self):
        paths = allPaths("resources/themes")
        self.lstThemes.clear()
        
        for p in paths:
            lst = [i for i in os.listdir(p) if os.path.splitext(i)[1] == ".theme"]
            for t in lst:
                theme = os.path.join(p, t)
                editable = not appPath() in theme
                n = self.getThemeName(theme)
                
                item = QListWidgetItem(n)
                item.setData(Qt.UserRole, theme)
                item.setData(Qt.UserRole+1, editable)
                
                thumb = os.path.join(p, t.replace(".theme", ".jpg"))
                px = QPixmap(200, 120)
                px.fill(Qt.white)
                if not os.path.exists(thumb):
                    thumb = self.createPreview(theme)
                    
                icon = QPixmap(thumb).scaled(200, 120, Qt.KeepAspectRatio)
                painter = QPainter(px)
                painter.drawPixmap(px.rect().center()-icon.rect().center(), icon)
                painter.end()
                item.setIcon(QIcon(px))
                
                self.lstThemes.addItem(item)
        self.lstThemes.setIconSize(QSize(200, 120))
                
    def getThemeName(self, theme):
        settings = QSettings(theme, QSettings.IniFormat)
        
        if settings.contains("Name"):
            return settings.value("Name")
        else:
            return os.path.splitext(os.path.split(theme)[1])[0]
        
    def loadTheme(self, theme):
        self._editingTheme = theme
        self._loadingTheme = True  # So we don't generate preview while loading
        
        # Load datas
        self.loadThemeDatas(theme)
        
        # Window Background
        self.btnThemWindowBackgroundColor.clicked.connect(lambda: self.getThemeColor("Background/Color"))
        try:
            self.cmbThemeBackgroundImage.disconnect()
        except:
            pass
        self.populatesCmbBackgrounds(self.cmbThemeBackgroundImage)
        self.cmbThemeBackgroundImage.currentIndexChanged.connect(self.updateThemeBackground)
        self.cmbThemBackgroundType.currentIndexChanged.connect(lambda i: self.setSetting("Background/Type", i))
        
        # Text Background
        self.btnThemeTextBackgroundColor.clicked.connect(lambda: self.getThemeColor("Foreground/Color"))
        self.spnThemeTextBackgroundOpacity.valueChanged.connect(lambda v: self.setSetting("Foreground/Opacity", v))
        self.spnThemeTextMargins.valueChanged.connect(lambda v: self.setSetting("Foreground/Margin", v))
        self.spnThemeTextPadding.valueChanged.connect(lambda v: self.setSetting("Foreground/Padding", v))
        self.cmbThemeTextPosition.currentIndexChanged.connect(lambda i: self.setSetting("Foreground/Position", i))
        self.spnThemeTextRadius.valueChanged.connect(lambda v: self.setSetting("Foreground/Rounding", v))
        self.spnThemeTextWidth.valueChanged.connect(lambda v: self.setSetting("Foreground/Width", v))
        
        # Text Options
        self.btnThemeTextColor.clicked.connect(lambda: self.getThemeColor("Text/Color"))
        self.cmbThemeFont.currentFontChanged.connect(self.updateThemeFont)
        try:
            self.cmbThemeFontSize.currentIndexChanged.disconnect(self.updateThemeFont)
        except:
            pass
        self.populatesFontSize()
        self.cmbThemeFontSize.currentIndexChanged.connect(self.updateThemeFont)
        self.btnThemeMisspelledColor.clicked.connect(lambda: self.getThemeColor("Text/Misspelled"))
        
        # Paragraph Options
        self.chkThemeIndent.stateChanged.connect(lambda v: self.setSetting("Spacings/IndendFirstLine", v!=0))
        self.cmbThemeLineSpacing.currentIndexChanged.connect(self.updateLineSpacing)
        self.cmbThemeLineSpacing.currentIndexChanged.connect(self.updateLineSpacing)
        self.spnThemeLineSpacing.valueChanged.connect(lambda v: self.setSetting("Spacings/LineSpacing", v))
        self.spnThemeParaAbove.valueChanged.connect(lambda v: self.setSetting("Spacings/ParagraphAbove", v))
        self.spnThemeParaBelow.valueChanged.connect(lambda v: self.setSetting("Spacings/ParagraphBelow", v))
        self.spnThemeTabWidth.valueChanged.connect(lambda v: self.setSetting("Spacings/TabWidth", v))
        
        # Update UI
        self.updateUIFromTheme()
        
        # Generate preview
        self._loadingTheme = False
        self.updatePreview()
        
    def loadThemeDatas(self, theme):
        settings = QSettings(theme, QSettings.IniFormat)
        self._themeData = {}
        
        # Theme name
        self._themeData["Name"] = self.getThemeName(theme)
        
        # Window Background
        self.loadSetting(settings, "Background/Color", "#000000")
        self.loadSetting(settings, "Background/ImageFile", "")
        self.loadSetting(settings, "Background/Type", 0)
        
        # Text Background
        self.loadSetting(settings, "Foreground/Color", "#ffffff")
        self.loadSetting(settings, "Foreground/Opacity", 50)
        self.loadSetting(settings, "Foreground/Margin", 40)
        self.loadSetting(settings, "Foreground/Padding", 10)
        self.loadSetting(settings, "Foreground/Position", 1)
        self.loadSetting(settings, "Foreground/Rounding", 5)
        self.loadSetting(settings, "Foreground/Width", 700)
        
        # Text Options
        self.loadSetting(settings, "Text/Color", "#ffffff")
        self.loadSetting(settings, "Text/Font", qApp.font().toString())
        self.loadSetting(settings, "Text/Misspelled", "#ff0000")
        
        # Paragraph Options
        self.loadSetting(settings, "Spacings/IndendFirstLine", False)
        self.loadSetting(settings, "Spacings/LineSpacing", 100)
        self.loadSetting(settings, "Spacings/ParagraphAbove", 0)
        self.loadSetting(settings, "Spacings/ParagraphBelow", 0)
        self.loadSetting(settings, "Spacings/TabWidth", 48)
        
    def loadSetting(self, settings, key, default):
        if settings.contains(key):
            self._themeData[key] = type(default)(settings.value(key))
        else:
            self._themeData[key] = default
        
    def setSetting(self, key, val):
        self._themeData[key] = val
        self.updatePreview()
        
    def updateUIFromTheme(self):
        self.txtThemeName.setText(self._themeData["Name"])
        
        # Window Background
        self.setButtonColor(self.btnThemWindowBackgroundColor, self._themeData["Background/Color"])
        i = self.cmbThemeBackgroundImage.findData(self._themeData["Background/ImageFile"], flags=Qt.MatchContains)
        if i != -1:
            self.cmbThemeBackgroundImage.setCurrentIndex(i)
        self.cmbThemBackgroundType.setCurrentIndex(self._themeData["Background/Type"])
        
        # Text background
        self.setButtonColor(self.btnThemeTextBackgroundColor, self._themeData["Foreground/Color"])
        self.spnThemeTextBackgroundOpacity.setValue(self._themeData["Foreground/Opacity"])
        self.spnThemeTextMargins.setValue(self._themeData["Foreground/Margin"])
        self.spnThemeTextPadding.setValue(self._themeData["Foreground/Padding"])
        self.cmbThemeTextPosition.setCurrentIndex(self._themeData["Foreground/Position"])
        self.spnThemeTextRadius.setValue(self._themeData["Foreground/Rounding"])
        self.spnThemeTextWidth.setValue(self._themeData["Foreground/Width"])
        
        # Text Options
        self.setButtonColor(self.btnThemeTextColor, self._themeData["Text/Color"])
        f = QFont()
        f.fromString(self._themeData["Text/Font"])
        self.cmbThemeFont.setCurrentFont(f)
        i = self.cmbThemeFontSize.findText(str(f.pointSize()))
        if i != -1:
            self.cmbThemeFontSize.setCurrentIndex(i)
        else:
            self.cmbThemeFontSize.addItem(str(f.pointSize()))
            self.cmbThemeFontSize.setCurrentIndex(self.cmbThemeFontSize.count()-1)
        self.setButtonColor(self.btnThemeMisspelledColor, self._themeData["Text/Misspelled"])
        
        # Paragraph Options
        self.chkThemeIndent.setCheckState(Qt.Checked if self._themeData["Spacings/IndendFirstLine"] else Qt.Unchecked)
        self.spnThemeLineSpacing.setEnabled(False)
        if self._themeData["Spacings/LineSpacing"] == 100:
            self.cmbThemeLineSpacing.setCurrentIndex(0)
        elif self._themeData["Spacings/LineSpacing"] == 150:
            self.cmbThemeLineSpacing.setCurrentIndex(1)
        elif self._themeData["Spacings/LineSpacing"] == 200:
            self.cmbThemeLineSpacing.setCurrentIndex(2)
        else:
            self.cmbThemeLineSpacing.setCurrentIndex(3)
            self.spnThemeLineSpacing.setEnabled(True)
            self.spnThemeLineSpacing.setValue(self._themeData["Spacings/LineSpacing"])
        self.spnThemeParaAbove.setValue(self._themeData["Spacings/ParagraphAbove"])
        self.spnThemeParaBelow.setValue(self._themeData["Spacings/ParagraphBelow"])
        self.spnThemeTabWidth.setValue(self._themeData["Spacings/TabWidth"])
        
    def populatesFontSize(self):
        self.cmbThemeFontSize.clear()
        s = list(range(6, 13)) + list(range(14,29, 2)) + [36, 48, 72]
        for i in s:
            self.cmbThemeFontSize.addItem(str(i))
        
    def updateThemeFont(self, v):
        f = self.cmbThemeFont.currentFont()
        s = self.cmbThemeFontSize.itemText(self.cmbThemeFontSize.currentIndex())
        if s:
            f.setPointSize(int(s))
            
        self._themeData["Text/Font"] = f.toString()
        self.updatePreview()
        
    def updateLineSpacing(self, i):
        if i == 0:
            self._themeData["Spacings/LineSpacing"] = 100
        elif i == 1:
            self._themeData["Spacings/LineSpacing"] = 150
        elif i == 2:
            self._themeData["Spacings/LineSpacing"] = 200
        elif i == 3:
            self._themeData["Spacings/LineSpacing"] = self.spnThemeLineSpacing.value()
        self.spnThemeLineSpacing.setEnabled(i == 3)
        self.updatePreview()
        
    def updateThemeBackground(self, i):
        img = self.cmbCorkImage.itemData(i)
        
        if img:
            self._themeData["Background/ImageFile"] = os.path.split(img)[1]
        else:
            self._themeData["Background/ImageFile"] = ""
        self.updatePreview()
        
    def getThemeColor(self, key):
        color = self._themeData[key]
        self.colorDialog = QColorDialog(QColor(color), self)
        color = self.colorDialog.getColor(QColor(color))
        if color.isValid():
            self._themeData[key] = color.name()
            self.updateUIFromTheme()
            self.updatePreview()
        
    def updatePreview(self):
        if self._loadingTheme:
            return
        
        px = self.createPreview(self._editingTheme, self.lblPreview.size())
        self.lblPreview.setPixmap(px)
        
    def createPreview(self, theme, size=QSize(200, 120)):
        pixmap = self.getPixmapFromTheme(theme)
        
        px = QPixmap(pixmap).scaled(size, Qt.KeepAspectRatio)
        
        w = px.width() / 10
        h = px.height() / 10
        r = self.textRect()
        
        painter = QPainter(px)
        painter.drawPixmap(QRect(w, h, w*4, h*5), pixmap, QRect(r.topLeft() - QPoint(w/3, h/3), QSize(w*4, h*5)))
        painter.setPen(Qt.white)
        painter.drawRect(QRect(w, h, w*4, h*5))
        painter.end()
        
        return px
        
    def setButtonColor(self, btn, color):
        btn.setStyleSheet("background:{};".format(color))
        
    def saveTheme(self):
        settings = QSettings(self._editingTheme, QSettings.IniFormat)
        
        self._themeData["Name"] = self.txtThemeName.text()
        for key in self._themeData:
            settings.setValue(key, self._themeData[key])
            
        settings.sync()
        self.populatesThemesList()
        self.themeStack.setCurrentIndex(0)
        self._editingTheme = None
        
    def cancelEdit(self):
        self.themeStack.setCurrentIndex(0)
        self._editingTheme = None
        
    def getPixmapFromTheme(self, theme):
        
        if not self._editingTheme:
            self.loadThemeDatas(theme)
        
        currentScreen = qApp.desktop().screenNumber(self)
        screen = qApp.desktop().screenGeometry(currentScreen)
        
        # Window Background
        px = QPixmap(screen.size())
        px.fill(QColor(self._themeData["Background/Color"]))
        
        painter = QPainter(px)
        if self._themeData["Background/ImageFile"]:
            path = findBackground(self._themeData["Background/ImageFile"])
            _type =self._themeData["Background/Type"]
            if path and _type > 0:
                if _type == 1: # Tiled
                    painter.fillRect(screen, QBrush(QImage(path)))
                else:
                    img = QImage(path)
                    scaled = img.size()
                    if _type == 3: # Stretched
                        scaled.scale(screen.size(), Qt.IgnoreAspectRatio)
                    elif _type == 4: # Scaled
                        scaled.scale(screen.size(), Qt.KeepAspectRatio)
                    elif _type == 5: # Zoomed
                        scaled.scale(screen.size(), Qt.KeepAspectRatioByExpanding)
                        
                    painter.drawImage((screen.width() - scaled.width()) / 2, (screen.height() - scaled.height()) / 2, img.scaled(scaled))
                    
        # Text Background
        textRect = self.textRect()
        
        painter.save()
        color = QColor(self._themeData["Foreground/Color"])
        color.setAlpha(self._themeData["Foreground/Opacity"] * 255 / 100)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        r = self._themeData["Foreground/Rounding"]
        painter.drawRoundedRect(textRect, r, r)
        painter.restore()
        
        painter.end()
        
        # Text
        padding = self._themeData["Foreground/Padding"]
        x = textRect.x() + padding
        y = textRect.y() + padding + self._themeData["Spacings/ParagraphAbove"]
        width = textRect.width() - 2 * padding
        height = textRect.height() - 2 * padding - self._themeData["Spacings/ParagraphAbove"]
        self.previewText.setGeometry(x, y, width, height)
        
        p = self.previewText.palette()
        p.setBrush(QPalette.Base, QBrush(px.copy(x, y, width, height)))
        p.setColor(QPalette.Text, QColor(self._themeData["Text/Color"]))
        p.setColor(QPalette.Highlight, QColor(self._themeData["Text/Color"]))
        p.setColor(QPalette.HighlightedText, Qt.black if qGray(QColor(self._themeData["Text/Color"]).rgb()) > 127 else Qt.white)
        self.previewText.setPalette(p)
        
        bf = QTextBlockFormat()
        bf.setLineHeight(self._themeData["Spacings/LineSpacing"], QTextBlockFormat.ProportionalHeight)
        bf.setTextIndent(self._themeData["Spacings/TabWidth"] * 1 if self._themeData["Spacings/IndendFirstLine"] else 0)
        bf.setTopMargin(self._themeData["Spacings/ParagraphAbove"])
        bf.setBottomMargin(self._themeData["Spacings/ParagraphBelow"])
        
        b = self.previewText.document().firstBlock()
        cursor = self.previewText.textCursor()
        while b.isValid():
            bf2 = b.blockFormat()
            bf2.merge(bf)
            cursor.setPosition(b.position())
            #cursor.setPosition(b.position(), QTextCursor.KeepAnchor)
            cursor.setBlockFormat(bf2)
            b = b.next()
        
        self.previewText.setTabStopWidth(self._themeData["Spacings/TabWidth"])
        self.previewText.document().setIndentWidth(self._themeData["Spacings/TabWidth"])
        
        f = QFont()
        f.fromString(self._themeData["Text/Font"])
        self.previewText.setFont(f)
        
        self.previewText.render(px, self.previewText.pos())
        return px
        
        
        ## Text Background
        ##self._themeData["Foreground/Color"]
        ##self._themeData["Foreground/Opacity"]
        ##self._themeData["Foreground/Margin"]
        ##self._themeData["Foreground/Padding"]
        ##self._themeData["Foreground/Position"]
        ##self._themeData["Foreground/Rounding"]
        ##self._themeData["Foreground/Width"]
        
        ## Text Options
        ##self._themeData["Text/Color"]
        ##self._themeData["Text/Font"]
        #self._themeData["Text/Misspelled"]
        
        ## Paragraph Options
        ##self._themeData["Spacings/IndendFirstLine"]
        ##self._themeData["Spacings/LineSpacing"]
        ##self._themeData["Spacings/ParagraphAbove"]
        ##self._themeData["Spacings/ParagraphBelow"]
        ##self._themeData["Spacings/TabWidth"]
        
    def textRect(self):
        currentScreen = qApp.desktop().screenNumber(self)
        screen = qApp.desktop().screenGeometry(currentScreen)
        
        margin = self._themeData["Foreground/Margin"]
        x = 0
        y = margin
        width = min(self._themeData["Foreground/Width"], screen.width() - 2 * margin)
        height = screen.height() - 2 * margin
        
        if self._themeData["Foreground/Position"] == 0:  # Left
            x = margin
        elif self._themeData["Foreground/Position"] == 1:  # Center
            x = (screen.width() - width) / 2
        elif self._themeData["Foreground/Position"] == 2:  # Right
            x = screen.width() - margin - width
        elif self._themeData["Foreground/Position"] == 3:  # Stretched
            x = margin
            width = screen.width() - 2 * margin
        return QRect(x, y, width, height)
    
    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        if self._editingTheme:
            self.updatePreview()