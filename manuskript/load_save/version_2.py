import string, zipfile, os, shutil, re
from logging import getLogger
from pathlib import Path
from PyQt5.QtCore import QModelIndex, QStandardPaths, Qt, QSettings
from PyQt5.QtWidgets import QListWidgetItem, qApp
from PyQt5.QtGui import QStandardItem, QColor, QStandardItemModel
from hashlib import blake2b

from manuskript import settings, ET
from manuskript.enums import Character as CharacterEnum, World, Plot, PlotStep, Outline, IntEnum
from manuskript.functions import mainWindow, iconColor, iconFromColorString, MainWindow
from manuskript.converters import HTML2PlainText

from manuskript.models.characterModel import CharacterInfo, Character
from manuskript.models import outlineItem
from manuskript.ui.listDialog import ListDialog
from typing import Literal, overload, OrderedDict, Iterable

hashes:dict[str, str]={}
def getHashes():
    mw=mainWindow()
    if mw is None or mw.currentProject is None:
        return
    settings=QSettings()
    settings.beginGroup('Project/{}'.format(mw.currentProject))
    hashes:dict=settings.value('hashes', {}, dict)
    return hashes
def setHashes(hashes:dict|None=None):
    mw=mainWindow()
    if mw is None or mw.currentProject is None:
        return
    if hashes is None and (hashes:=getHashes()) is None:
        return
    settings=QSettings()
    settings.beginGroup('Project/{}'.format(mw.currentProject))
    settings.setValue('hashes', hashes)
    return hashes
def fetchHashes(path:str|Path|None=None, base=None):
    if path is None:
        mw=mainWindow()
        if mw is None or mw.currentProject is None:
            return
        path=Path(mw.currentProject)
    if base is None:
        base=path
    path=Path(path)
    base=Path(base)
    for p in path.iterdir():
        if p.is_dir():
            yield from fetchHashes(p, base)
        else:
            try:
                yield (p.relative_to(base).as_posix(), blake2b(p.read_bytes()).hexdigest())
            except Exception:
                #If its unreadeable, we need a placeholder
                yield (p.relative_to(base).as_posix(), blake2b(p.__bytes__()).hexdigest())
def compareHashes():
    oldHashes=getHashes()
    if oldHashes is None:
        return
    newHashes=dict(fetchHashes())
    changed:list[str]=[]
    for key, value in oldHashes.items():
        if newHashes.get(key) != value:# Will also include deleted items
            changed.append(key)
    changed.extend(set(newHashes).difference(oldHashes))
    return changed
    

LOGGER = getLogger(__name__)
_parser = ET.hugeparser()

try:
    import zlib  # Used with zipfile for compression
    compression = zipfile.ZIP_DEFLATED
except ImportError:
    compression = zipfile.ZIP_STORED
characterMap:OrderedDict[Literal['Name', 'ID', 'Importance', 'POV', 'Motivation', 'Goal', 'Conflict', 'Epiphany', 'Phrase Summary', 'Paragraph Summary', 'Full Summary', 'Notes']|str, CharacterEnum] = OrderedDict([
    ("Name", CharacterEnum.name),
    ("ID",CharacterEnum.ID),
    ("Importance",CharacterEnum.importance),
    ("POV",CharacterEnum.pov),
    ("Motivation",CharacterEnum.motivation),
    ("Goal",CharacterEnum.goal),
    ("Conflict",CharacterEnum.conflict),
    ("Epiphany",CharacterEnum.epiphany),
    ("Phrase Summary",CharacterEnum.summarySentence),
    ("Paragraph Summary",CharacterEnum.summaryPara),
    ("Full Summary",CharacterEnum.summaryFull),
    ("Notes",CharacterEnum.notes)
]) # pyright: ignore[reportAssignmentType] 
cache:dict[str, str|bytes] = {}
class Project:
    tabLength=10
    _mw=None
    format="1"
    def __init__(self, project:str|None=None, tabLength:None|int=10, zip=None) -> None:
        if isinstance(tabLength, int):
            self.tabLength=tabLength
        self.zip=zip
        self.project=project
    @property
    def mw(self)->MainWindow:
        if self._mw:
            return self._mw
        self.__class__._mw=self._mw=mainWindow()
        return self._mw
    @staticmethod
    def slugify(name:str)->str:
        """
        A basic slug function, that escapes all spaces to "_" and all non letters/digits to "-".
        @param name: name to slugify (str)
        @return: str
        """
        valid = string.ascii_letters + string.digits
        newName = ""
        for c in name:
            if c in valid:
                newName += c
            elif c in string.whitespace:
                newName += "_"
            else:
                newName += "-"
        return newName
    def loadProject(self):
        pass
    def saveProject(self, zip=None):
        pass
    @staticmethod
    def loadFilesFromZip(zipname):
        """Returns the content of zipfile as a dict of filename:content."""
        zf = zipfile.ZipFile(zipname)
        files:dict[str, bytes] = {}
        for f in zf.namelist():
            # Some archiving programs (e.g. 7-Zip) also store entries for the directories when
            # creating an archive. We have no use for these entries; skip them entirely.
            if not f.strip().endswith('/'):
                files[os.path.normpath(f)] = zf.read(f)
        return files
    @classmethod
    def mainWindow(cls)->MainWindow:
        if cls._mw:
            return cls._mw
        cls._mw=mainWindow()
        return cls._mw
    def permissionError(self, filesWithPermissionErrors:list[str], keyword='saved'):
        if len(filesWithPermissionErrors) > 0:
            dlg = ListDialog(self.mw)
            dlg.setModal(True)
            dlg.setWindowTitle(dlg.tr(f"Files not {keyword}"))
            dlg.label.setText(dlg.tr(f"The following files were not {keyword} and appear to be open in another program"))
            for f in filesWithPermissionErrors:
                QListWidgetItem(f, dlg.listWidget)
            dlg.open()
            return True
        return False
    @classmethod
    def LoadFromMsk(cls, project:str,tabLength:None|int=10, zip=None):
        projectPath=Path(project)
        path= projectPath.joinpath('MANUSKRIPT')
        match path.read_text().strip():
            case '0':
                cls=V0Project
                return V0Project(project=project, tabLength=tabLength, zip=zip)
            case '1':
                cls=V1Project
            case _:
                #Check for version specific files in hopes of determining the version, hopefully we get a good answer
                v0Files=['settings.pickle', 'flatModel.xml', 'world.xml', 'labels.xml', 'status.xml',  'outline.xml']
                v1Files=['infos.txt', 'labels.txt',  'revisions.xml', 'settings.txt', 'status.txt', 'summary.txt', 'world.opml']
                def vToPaths(files):
                    return tuple(projectPath.joinpath(file).exists() for file in  files)
                v0= vToPaths(v0Files).count(True)
                v1= vToPaths(v1Files).count(True)
                if v1>=v0:
                    cls=V1Project
                else:
                    cls=V0Project
        return cls(project=project, tabLength=tabLength, zip=zip)
    @staticmethod
    def savetozip(files:list[tuple[str, str|bytes]], project:str|Path):
        try:
            zf = zipfile.ZipFile(project, mode="w")
            for filename, content in files:
                zf.writestr(filename, content, compress_type=compression)
            zf.close()
            return True
        except:
            return False
class V1Project(Project):
    def formatMetaData(self,name:str, value:str|dict, tabLength:int|None=None):
        if tabLength == None:
            tabLength=self.tabLength
        if isinstance(value, dict):
            tab=(" " * tabLength) +'\n'
            vals=[]
            for valname, val in value.items():
                vals.append(self.formatMetaData(valname, val, tabLength))
            value='\n'+tab.join(vals)
        # else:
        value=str(value)
        # Multiline formatting
        if len(value.split("\n")) > 1:
            value = "\n".join([" " * (tabLength + 1) + l for l in value.split("\n")])[tabLength + 1:]
        # Avoid empty description (don't know how much MMD loves that)
        name=str(name)
        if name == "":
            name = "None"
        # Escapes ":" in name
        name = name.replace(":", "_.._")
        spaces=" " * (tabLength - (len(name)+1))
        return f"{name}: {spaces}{value}\n"
    def addTextItems(self,mdl, odict, parent=None):
        """
        Adds a text / outline items from an OrderedDict.
        @param mdl: model to add to
        @param odict: OrderedDict
        @return: nothing
        """
        if parent is None:
            parent = mdl.rootItem

        for k in odict:

            # In case k is a folder:
            if (type(odict[k]) == OrderedDict) and ("folder.txt" in odict[k]):

                # Adds folder
                LOGGER.debug("{}* Adds {} to {} (folder)".format("  " * parent.level(), k, parent.title()))
                item = self.outlineFromMMD(odict[k]["folder.txt"], parent=parent)
                item._lastPath = odict[k + ":lastPath"]

                # Read content
                self.addTextItems(mdl, odict[k], parent=item)

            if (":lastPath" in k) or (k == "folder.txt"):
                continue

            # k is not a folder
            if type(odict[k]) == str:
                try:
                    LOGGER.debug("{}* Adds {} to {} (file)".format("  " * parent.level(), k, parent.title()))
                    item = self.outlineFromMMD(odict[k], parent=parent)
                    item._lastPath = odict[k + ":lastPath"]
                except KeyError:
                    LOGGER.error(f"Failed to add file {k}")
            else:
                LOGGER.debug(f"Strange things in file {k}")
    def addWorldItem(self,root, mdl, parent=QModelIndex()):
        """
        Lists elements in a world model and create an OPML xml file.
        @param root: an Etree element
        @param mdl:  a worldModel
        @param parent: the parent index in the world model
        @return: root, to which sub element have been added
        """
        # List every row (every world item)
        for x in range(mdl.rowCount(parent)):
            # For each row, create an outline item.
            outline = ET.SubElement(root, "outline")
            for y in range(mdl.columnCount(parent)):
                val = mdl.data(mdl.index(x, y, parent))
                if not val:
                    continue
                for w in World:
                    if y == w.value:
                        outline.attrib[w.name] = val
                if mdl.hasChildren(mdl.index(x, y, parent)):
                    self.addWorldItem(outline, mdl, mdl.index(x, y, parent))
        return root
    def outlineFromMMD(self,text, parent):
        """
        Creates outlineItem from multimarkdown file.
        @param text: content of the file
        @param parent: appends item to parent (outlineItem)
        @return: outlineItem
        """
        md, body = self.parseMMDFile(text, asDict=True)

        # Assign ID on creation, to avoid generating a new ID for this object
        item = outlineItem(parent=parent, ID=md.pop('ID'))

        # Store metadata
        for k in md:
            if k in Outline.__members__:
                item.setData(Outline.__members__[k], str(md[k]))

        # Store body
        item.setData(Outline.text, str(body))

        # Set file format to "md"
        # (Old version of manuskript had different file formats: text, t2t, html and md)
        # If file format is html, convert to plain text:
        if item.type() == "html":
            item.setData(Outline.text, HTML2PlainText(body))
        if item.type() in ["txt", "t2t", "html"]:
            item.setData(Outline.type, "md")

        return item
    @staticmethod
    def addPlotItem(root, mdl, parent=QModelIndex()):
        """
        Lists elements in a plot model and create an xml file.
        @param root: an Etree element
        @param mdl:  a plotModel
        @param parent: the parent index in the plot model
        @return: root, to which sub element have been added
        """
        # List every row (every plot item)
        for x in range(mdl.rowCount(parent)):
            # For each row, create an outline item.
            outline = ET.SubElement(root, "plot")
            for y in range(mdl.columnCount(parent)):

                index = mdl.index(x, y, parent)
                val = mdl.data(index)
                #
                # if not val:
                #     continue
                for w in Plot:
                    if y == w.value and val:
                        outline.attrib[w.name] = val
                # List characters as attrib
                if y == Plot.characters:
                    if mdl.hasChildren(index):
                        characters = []
                        for cX in range(mdl.rowCount(index)):
                            for cY in range(mdl.columnCount(index)):
                                cIndex = mdl.index(cX, cY, index)
                                characters.append(mdl.data(cIndex))
                        outline.attrib[Plot.characters.name] = ",".join(characters)
                    elif Plot.characters.name in outline.attrib:
                        outline.attrib.pop(Plot.characters.name)
                # List resolution steps as sub items
                elif y == Plot.steps:
                    if mdl.hasChildren(index):
                        for cX in range(mdl.rowCount(index)):
                            step = ET.SubElement(outline, "step")
                            for cY in range(mdl.columnCount(index)):
                                cIndex = mdl.index(cX, cY, index)
                                # If empty, returns None, which creates trouble later with lxml, so default to ""
                                val = mdl.data(cIndex) or ""
                                for w in PlotStep:
                                    if cY == w.value and w.name:
                                        step.attrib[w.name] = val
                    elif Plot.steps.name in outline.attrib:
                        outline.attrib.pop(Plot.steps.name)
        return root
    def exportOutlineItem(self,root:outlineItem|None=None,files:list|None = None, moves:list|None  = None, removes:list|None  = None)->tuple[list[tuple[str,str]],list[tuple[str,str]],list[str]]:
        """
        Takes an outline item, and returns three lists:
        1. of (`filename`, `content`), representing the whole tree of files to be written, in multimarkdown.
        2. of (`lastfilename`, `newfilename`) listing files to be moved
        3. of `filename`, representing files to be removed.

        @param root: OutlineItem
        @return: [(str, str)], [(str, str)], [str]
        """
        if root is None:
            root=mainWindow().mdlOutline.rootItem
        if files is None:
            files=[]
        if removes is None:
            removes=[]
        if moves is None:
            moves=[]

        for child in root.children():
            spath = os.path.join(*self.outlineItemPath(child))
            # Has the item been renamed?
            lp = child._lastPath
            if lp and spath != lp:
                moves.append((lp, spath))
                LOGGER.debug("%s has been renamed (%s → %s)", child.title(), lp,  spath)
                LOGGER.debug(" → We mark for moving: %s", lp)
            # Updates item last's path
            child._lastPath = spath
            # Generating content
            if child.type() == "folder":
                spath = os.path.join(spath, "folder.txt")
            content = self.outlineToMMD(child)
            files.append((spath, content))
            self.exportOutlineItem(child, files=files, moves=moves, removes=removes)
        return files, moves, removes
    def outlineItemPath(self,item:outlineItem)->list[str]:
        """
        Returns the outlineItem file path (like the path where it will be written on the disk). As a list of folder's
        name. To be joined by os.path.join.
        @param item: outlineItem
        @return: list of folder's names
        """
        # Root item
        parent=item.parent()
        if not parent:
            return ["outline"]
        else:
            # Count the number of siblings for padding '0'
            siblings = parent.childCount()
            
            # We check if multiple items have the same name
            # If so, we add "-ID" to their name
            siblingsNames = [s.title() for s in parent.children()]
            if siblingsNames.count(item.title()) > 1:
                title = "{}-{}".format(item.title(), item.ID())
            else:
                title = item.title()
            ID=str(item.row()).zfill(len(str(siblings)))
            name = f"{ID}-{self.slugify(title)}{'' if item.type() == 'folder' else '.md'}"
            return self.outlineItemPath(parent) + [name]
    def outlineToMMD(self,item):
        content = ""
        # We don't want to write some datas (computed)
        exclude = [Outline.wordCount, Outline.goal, Outline.goalPercentage, Outline.revisions, Outline.text]
        # We want to force some data even if they're empty
        force = [Outline.compile]
        for attrib in Outline:
            if attrib in exclude:
                continue
            val = item.data(attrib.value)
            if val or attrib in force:
                content += self.formatMetaData(attrib.name, str(val), 15)
        content += "\n\n"
        content += item.data(Outline.text)
        return content
    def appendRevisions(self,mdl, root):
        """
        Parse etree item to find outlineItem's with revisions, and adds them to model `mdl`.
        @param mdl: outlineModel
        @param root: etree
        @return: nothing
        """
        for child in root:
            # Recursively go through items
            if child.tag == "outlineItem":
                self.appendRevisions(mdl, child)

            # Revision found.
            elif child.tag == "revision":
                # Get root's ID
                ID = root.attrib["ID"]
                if not ID:
                    LOGGER.debug("* Serious problem: no ID!")
                    LOGGER.error("Revision has no ID associated!")
                    continue

                # Find outline item in model
                item = getattr(mdl,'getItemByID', lambda *a:None)(ID)
                if not item:
                    LOGGER.debug("* Error: no item whose ID is %s", ID)
                    LOGGER.error("Could not identify the item matching the revision ID.")
                    continue

                # Store revision
                LOGGER.debug("* Appends revision ({}) to {}".format(child.attrib["timestamp"], item.title()))
                item.appendRevision(child.attrib["timestamp"], child.attrib["text"])
    def getOutlineItem(self,item, enum):
        """
        Reads outline items from an opml file. Returns a row of QStandardItem, easy to add to a QStandardItemModel.
        @param item: etree item
        @param enum: enum to read keys from
        @return: [QStandardItem]
        """
        row = self.getStandardItemRowFromXMLEnum(item, enum)
        LOGGER.debug("* Add worldItem: %s", row[0].text())
        for child in item:
            sub = self.getOutlineItem(child, enum)
            row[0].appendRow(sub)
        return row
    @staticmethod
    def getStandardItemRowFromXMLEnum(item, enum:type[IntEnum])->list[QStandardItem]:
        """
        Reads and etree item and creates a row of QStandardItems by cross-referencing an enum.
        Returns a list of QStandardItems that can be added to a QStandardItemModel by appendRow.
        @param item: the etree item
        @param enum: the enum
        @return: list of QStandardItems
        """
        row = []
        
        for _ in range(len(enum)):
            row.append(QStandardItem(""))
        for name in item.attrib:
            if name in enum.__members__:
                row[enum[name].value] = QStandardItem(item.attrib[name])
        return row
    def saveProject(self,zip:bool|None|Literal['None']='None'):
        """
        Saves the project. If zip is False, the project is saved as a multitude of plain-text files for the most parts
        and some XML or zip? for settings and stuff.
        If zip is True, everything is saved as a single zipped file. Easier to carry around, but does not allow
        collaborative work, versioning, or third-party editing.
        @param zip: if True, saves as a single file. If False, saves as plain-text. If None, tries to determine based on settings.
        @return: True if successful, False otherwise.
        """
        if isinstance(zip, str):
            zip=self.zip
        if zip == None:
            zip = settings.saveToZip
        LOGGER.info("Saving to: %s", "zip" if zip else "folder")
        # List of files to be written
        files:list[tuple[str,str|bytes]] = []
        # List of files to be removed
        removes = []
        # List of files to be moved
        moves:list[tuple[str,str]]  = []
        # MainWindow interaction things.
        mw = self.mw
        project = mw.currentProject or self.project
        # Sanity check (see PR-583): make sure we actually have a current project.
        if project == None:
            LOGGER.error("Cannot save project because there is no current project in the UI.")
            return False

        # File format version
        files.append(("MANUSKRIPT", self.format))
        
        files.append(("infos.txt", self.infotext))

        ####################################################################################################################

        path = "summary.txt"
        files.append(("summary.txt", self.summarytext))

        files.append(("status.txt", self.statustext))
        files.append(("labels.txt", self.labelstext))

        ####################################################################################################################
        # Characters


        path = os.path.join("characters", "{name}.txt")
        mdl = mw.mdlCharacter

        # Review characters
        for c in mdl.characters:
            content = self.charactercontent(c)
            cpath = path.format(name=f"{c.ID()}-{self.slugify(c.name())}")
            # Has the character been renamed?
            if c.lastPath and cpath != c.lastPath:
                moves.append((c.lastPath, cpath))
            # Update character's path
            c.lastPath = cpath
            files.append((cpath, content))

        ####################################################################################################################
        # Texts
        # In an outline folder

        mdl = mw.mdlOutline

        # Go through the tree
        self.exportOutlineItem(mdl.rootItem, files=files, moves=moves, removes=removes)
        # Writes revisions (if asked for)
        if settings.revisions["keep"]:
            files.append(("revisions.xml", mdl.saveToXML()))
        ####################################################################################################################
        # World
        files.append(("world.opml", self.worldcontent))

        ####################################################################################################################
        # Plots 
        path = "plots.xml"
        files.append((path, self.plotcontent))

        ####################################################################################################################
        # Settings
        # Saved in readable text (json) for easier versioning. But they mustn't be shared, it seems.
        # Maybe include them only if zipped?
        # Well, for now, we keep them here...

        files.append(("settings.txt", settings.save(protocol=0)))

        # We check if the file exist and we have write access. If the file does
        # not exist, we check the parent folder, because it might be a new project.
        if os.path.exists(project) and not os.access(project, os.W_OK) or \
        not os.path.exists(project) and not os.access(os.path.dirname(project), os.W_OK):
            LOGGER.error("You don't have write access to save this project there.")
            return False

        ####################################################################################################################
        # Save to zip

        if zip:
            return self.savetozip(files, project)
        ####################################################################################################################
        # Save to plain text

        else:
            global cache
            filesWithPermissionErrors = list()
            # Project path
            dir:str = os.path.dirname(project)
            # Folder containing file: name of the project file (without .msk extension)
            folder:str = os.path.splitext(os.path.basename(project))[0]
            # Debug
            LOGGER.debug("Saving to folder %s ", folder)
            base=os.path.join(dir, folder)
            # If cache is empty (meaning we haven't loaded from disk), we wipe folder, just to be sure.
            if not cache and os.path.exists(base):
                shutil.rmtree(base)
            # Moving files that have been renamed
            for old, new in moves:
                # Get full path
                self.replacepath(old, new, base)

            # Writing files
            filesWithPermissionErrors.extend(self.writefiles(files, base))
            # Removing phantoms
            self.deletepaths(set(cache) - {p for p, c in files}, base)
            # Removing empty directories
            self.cleanemptydirs(base)
            # Write the project file's content
            try:
                with open(project, "wt", encoding="utf8", newline="\n") as f:
                    f.write(self.format)  # Format number
            except PermissionError as e:
                LOGGER.error("Cannot open file " + project + " for writing: " + (e.strerror or ''))
                filesWithPermissionErrors.append(project)
            self.permissionError(filesWithPermissionErrors)
            return project not in filesWithPermissionErrors
    

    @staticmethod
    def cleanemptydirs(base:str):
        for root, dirs, _ in os.walk(os.path.join(base, "outline")):
            for dir in dirs:
                newDir = os.path.join(root, dir)
                try:
                    os.removedirs(newDir)
                    LOGGER.debug("* Removing empty directory: %s", newDir)
                except:
                        # Directory not empty, we don't remove.
                    pass
    @staticmethod
    def deletepaths(paths:Iterable[str], base):
        for path in paths:
            filename = os.path.join(base, path)
            LOGGER.debug("* Removing %s", path)
            try:
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:  # elif os.path.exists(filename)
                    os.remove(filename)
                    # Clear cache
            except Exception:pass
            finally:
                cache.pop(path, 0)
    @staticmethod
    def writefiles(files, base)->list[str]:
        global cache
        for path, content in files:
            filesWithPermissionErrors=[]
            filename = os.path.join(base, path)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            # Check if content is in cache, and write if necessary
            if path not in cache or cache[path] != content:
                LOGGER.debug("* Writing file {} ({})".format(path, "not in cache" if path not in cache else "different"))
                try:
                    if isinstance(content,bytes|bytearray|memoryview):
                        with open(filename, "wb") as f:
                            f.write(content)
                    else:
                        with open(filename, "wt", encoding="utf8", newline="\n") as f:
                            f.write(content)
                    cache[path] = content
                except PermissionError as e:
                    LOGGER.error(f"Cannot open file {filename} for writing: {e.strerror}")
                    filesWithPermissionErrors.append(filename)
        return filesWithPermissionErrors
    @staticmethod
    def replacepath(old, new, base):
        "Move the old file to the new place and update cache"
        global cache
        try:
            oldPath = os.path.join(base, old)
            newPath = os.path.join(base, new)
            os.replace(oldPath, newPath)
            LOGGER.debug("* Renaming/moving {} to {}".format(old, new))
        except FileNotFoundError:
                    # Maybe parent folder has been renamed
            pass
        cache2 = {}
        for f in cache:
            f2 = f.replace(old, new)
            if f2 != f:
                LOGGER.debug("  * Updating cache: %s, %s", f, f2)
            cache2[f2] = cache[f]
        cache.clear()
        cache.update(cache2)
    @property
    def plotcontent(self):
        "Either in XML or lots of plain texts? More probably XML since there is not really a lot if writing to do (third-party)"
        root = ET.Element("root")
        self.addPlotItem(root, self.mw.mdlPlots)
        return ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    @property
    def worldcontent(self):
        "Either in an XML file, or in lots of plain texts?  More probably text, since there might be writing done in third-party."
        root = ET.Element("opml")
        root.attrib["version"] = "1.0"
        body = ET.SubElement(root, "body")
        self.addWorldItem(body, self.mw.mdlWorld)
        return  ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    def charactercontent(self,  c:Character):
        "Character content to be saved in a character folder"
        content = ""
        mdl=self.mw.mdlCharacter
        for value, m in characterMap.items():
            val = mdl.data(c.index(m.value))
            if isinstance(val,str):
                content += self.formatMetaData(value, val.strip(), 20)
        # Character's color:
        content += self.formatMetaData("Color", c.color().name(QColor.HexRgb), 20)

        # Character's infos
        for info in c.infos:
            content += self.formatMetaData(info.description, info.value, 20)
        return content
    @property
    def labelstext(self):
        "Label in plain text"
        return self.statusandlabels(self.mw.mdlLabels)
    @property
    def statustext(self):
        "Status in plain text"
        return self.statusandlabels(self.mw.mdlStatus)
    @staticmethod
    def statusandlabels(mdl):
        content = ""
        # We skip the first row, which is empty and transparent
        for i in range(1, mdl.rowCount()):
            color = ""
            if mdl.data(mdl.index(i, 0), Qt.ItemDataRole.DecorationRole) != None:
                color = iconColor(mdl.data(mdl.index(i, 0), Qt.ItemDataRole.DecorationRole)).name(QColor.HexRgb)
                color = color if color != "#ff000000" else "#00000000"
            text = mdl.data(mdl.index(i, 0))
            if text:
                start="" if color == "" else ":"
                content += f"{text}{start + " " * (20 - len(text)) + color}\n"
        return content
    @property
    def summarytext(self):
        "Summary in plain text, saved in summary.txt"
        content = ""
        for col,name in enumerate(("Situation","Sentence","Paragraph","Page","Full")):
            item = self.mw.mdlFlatData.item(1, col)
            if item:
                val = item.text().strip()
            else:
                val = ""
            if val:
                content += self.formatMetaData(name, val, 12)
        return content

    @property
    def infotext(self):
        "General infos (book and author) Saved in plain text, in infos.txt"
        content = ""
        for col, name in enumerate(("Title","Subtitle","Serie", "Volume","Genre","License","Author","Email")):
            item = self.mw.mdlFlatData.item(0, col)
            val = "" if not item else item.text().strip()
            if val:
                content += "{name}:{spaces}{value}\n".format(name=name,spaces=" " * (15 - len(name)),value=val)        
        return content
    ########################################################################################################################
    # LOAD
    ########################################################################################################################

    def loadProject(self,project:str='', zip='None')->list[str]:
        """
        Loads a project.
        @param project: the filename of the project to open.
        @param zip: whether the project is a zipped or not.
        @return: an array of errors, empty if None.
        """
        errors = list()
        filesWithPermissionErrors:list[str] = list()
        self.project=project=project if project or not isinstance(self.project, str) else self.project
        ####################################################################################################################
        # Read and store everything in a dict
        files:dict[str, str|bytes]|dict[str, str]={}
        LOGGER.debug("Loading {} ({})".format(project, "zip" if zip else "folder"))
        if isinstance(zip, str):
            zip=self.zip
        if zip:
            files.update(self.loadfromzip(project))
        else:
            errors, filesWithPermissionErrors=self.loadfromfolder(files)
            # Saves to cache (only if we loaded from disk and not zip)
            global cache
            cache.clear()
            cache.update(files)
            # FIXME: watch directory for changes, how well should we watch? do we just want to know something has changed?
            # 

        # Sort files by keys
        files = OrderedDict(sorted(files.items()))
        ####################################################################################################################
        # Settings
        if not self.loadsettings(files):
            errors.append("settings.txt")
        # Just to be sure
        settings.saveToZip = bool(zip)
        settings.defaultTextType = "md"

        ####################################################################################################################
        # Labels

        if not self.loadlabels(files):
            errors.append("labels.txt")

        ####################################################################################################################
        # Status

        if not self.loadstatus(files):
            errors.append("status.txt")

        ####################################################################################################################
        # Infos

        if not self.loadinfos(files):
            errors.append("infos.txt")

        ####################################################################################################################
        # Summary

        if not self.loadsummary(files):
            errors.append("summary.txt")


        ####################################################################################################################
        # Plots

        if not self.loadplots(files):
            errors.append("plots.xml")

        ####################################################################################################################
        # World

        if not self.loadworld(files):
            errors.append("world.opml")

        ####################################################################################################################
        # Characters

        self.loadcharacters(files)

        ####################################################################################################################
        # Texts
        # We read outline form the outline folder. If revisions are saved, then there's also a revisions.xml which contains
        # everything, but the outline folder takes precedence (in cases it's been edited outside of manuskript.

        self.loadoutline(files)
        # Adds revisions
        self.loadrevisions(files)
        mdl = self.mw.mdlOutline
        # Check IDS
        mdl.rootItem.checkIDs()
        self.permissionError(filesWithPermissionErrors, keyword='loaded')
        return errors

    def loadsettings(self, files):
        try:
            if "settings.txt" in files:
                settings.load(files["settings.txt"], fromString=True, protocol=0)
                return True
            return False
        except:
            return False

    def loadrevisions(self, files):
        mdl = self.mw.mdlOutline
        if "revisions.xml" in files:
            root = ET.fromstring(files["revisions.xml"], parser=_parser)
            self.appendRevisions(mdl, root)
        return True
    def loadoutline(self, files):
        """We read outline form the outline folder. If revisions are saved, then there's also a revisions.xml which contains
        everything, but the outline folder takes precedence in cases it's been edited outside of manuskript."""
        mdl = self.mw.mdlOutline
        LOGGER.debug("Reading outline:")
        paths = [f for f in files if "outline" in f]
        outline = OrderedDict()
        # We create a structure of imbricated OrderedDict to store the whole tree.
        for f in paths:
            split = f.split(os.path.sep)[1:]
            # LOGGER.debug("* %s", split)
            last = ""
            parent = outline
            parentLastPath = "outline"
            for i in split:
                if last:
                    parent = parent[last]
                    parentLastPath = os.path.join(parentLastPath, last)
                last = i
                if not i in parent:
                    # If not last item, then it is a folder
                    if i != split[-1]:
                        parent[i] = OrderedDict()

                    # If file, we store it
                    else:
                        parent[i] = files[f]

                    # We store f to add it later as lastPath
                    parent[i + ":lastPath"] = os.path.join(parentLastPath, i)

        # We now just have to recursively add items.
        self.addTextItems(mdl, outline)
        return True

    def loadcharacters(self, files:dict[str, str|bytes]):
        mdl = self.mw.mdlCharacter
        LOGGER.debug("Reading Characters:")
        for f in [f for f in files if "characters" in f]:
            md, body = self.parseMMDFile(files[f])
            c = mdl.addCharacter()
            c.lastPath = f
            color = False
            for desc, val in md:
                # Base infos
                if (key:=characterMap.get(desc)) is not None:
                    index = c.index(key.value)
                    mdl.setData(index, val)
                # Character color
                elif desc == "Color" and not color:
                    c.setColor(QColor(val))
                    # We remember the first time we found "Color": it is the icon color.
                    # If "Color" comes a second time, it is a Character's info.
                    color = True
                # Character's infos
                else:
                    c.infos.append(CharacterInfo(c, desc, val))
            LOGGER.debug("* Adds {} ({})".format(c.name(), c.ID()))
        return True

    def loadworld(self, files):
        mdl = self.mw.mdlWorld
        if "world.opml" in files:
            LOGGER.debug("Reading World:")
            # xml = bytearray(files["plots.xml"], "utf-8")
            root = ET.fromstring(files["world.opml"])
            body = root.find("body")
            if body is None:
                return False

            for outline in body:
                row = self.getOutlineItem(outline, World)
                mdl.appendRow(row)
            return True
        return False

    def loadplots(self, files):
        mdl = self.mw.mdlPlots
        if "plots.xml" in files:
            LOGGER.debug("Reading plots:")
            # xml = bytearray(files["plots.xml"], "utf-8")
            root = ET.fromstring(files["plots.xml"])
            for plot in root:
                    # Create row
                row = self.getStandardItemRowFromXMLEnum(plot, Plot)
                    # Log
                LOGGER.debug("* Add plot: %s", row[0].text())

                    # Characters
                if row[Plot.characters].text():
                    IDs = row[Plot.characters].text().split(",")
                    item = QStandardItem()
                    for ID in IDs:
                        item.appendRow(QStandardItem(ID.strip()))
                    row[Plot.characters] = item

                    # Subplots
                for step in plot:
                    row[Plot.steps].appendRow(self.getStandardItemRowFromXMLEnum(step, PlotStep))

                    # Add row to the model
                mdl.appendRow(row)
            return True
        return False
    @staticmethod
    def loadstatus(files):
        try:
            mdl = Project.mainWindow().mdlStatus
            mdl.appendRow(QStandardItem(""))  # Empty = No status
            if "status.txt" in files:
                LOGGER.debug("Reading status:")
                for s in files["status.txt"].split("\n"):
                    if not s:
                        continue
                    LOGGER.debug("* Add status: %s", s)
                    mdl.appendRow(QStandardItem(s))
                return True
            return False
        except:return False

    @staticmethod
    def loadlabels(files):
        try:
            mdl = Project.mainWindow().mdlLabels
            mdl.appendRow(QStandardItem(""))  # Empty = No labels
            if "labels.txt" in files:
                LOGGER.debug("Reading labels:")
                for s in files["labels.txt"].split("\n"):
                    if not s:continue
                    m = re.search(r"^(.*?):\s*(.*)$", s)
                    if not m:continue
                    txt = m.group(1)
                    col = m.group(2)
                    LOGGER.debug("* Add status: {} ({})".format(txt, col))
                    icon = iconFromColorString(col)
                    mdl.appendRow(QStandardItem(icon, txt))
                return True
            return False
        except:
            return False
    def loadfromfolder(self,files:dict[str,str|bytes]):
        errors:list[str]=[]
        filesWithPermissionErrors:list[str]=[]
        if self.project==None:
            return errors, filesWithPermissionErrors
        # Folder containing file: name of the project file (without .msk extension)
        folder = os.path.splitext(os.path.basename(self.project))[0]
        # The full path towards the folder containing files
        path = os.path.join(os.path.dirname(self.project), folder, "")
        basepath=Path(path)
        
        def skip(p:str|Path)->bool:
            p=p if isinstance(p, str) else p.name
            "skip  directories that begin with a period or if the basedir of the file starts with an '.' or filenames that begin with a period"
            return p.startswith(".") or os.path.basename(p).startswith(".")
        
        for dirpath, dirnames, filenames in basepath.walk():
            print(dirpath.relative_to(basepath, walk_up=True))
        for dirpath, dirnames, filenames in os.walk(path):
            p = dirpath.replace(path, "")
            if skip(p):
                continue
            for f in filenames:
                if skip(f):
                    continue
                if f.endswith((".xml", "opml")):
                    mode='rb'
                    enc=None
                else:
                    mode='r'
                    enc="utf8"
                try:
                    filename = os.path.join(dirpath, f)
                    with open(filename, mode, encoding=enc) as fo:
                        files[os.path.join(p, f)] = fo.read()
                except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError) as e:
                    LOGGER.error(f"Ignore file {filename} because of the error: {getattr(e,'reason', f'Unkown {e.__class__.__name__} error')}")
                except PermissionError as e:
                    LOGGER.error(f"Cannot open file  {filename}: {e.strerror}")
                    errors.append(filename)
                    filesWithPermissionErrors.append(filename)
        return errors, filesWithPermissionErrors
    @staticmethod
    def loadfromzip(project:str)->dict[str,str]:

        files:dict[str, str]={}
        for name, content in Project.loadFilesFromZip(project).items():
            if not name.endswith((".xml", "opml")):
                files[name] = content.decode("utf-8")
        return files
    def loadinfos(self,files):
        if "infos.txt" in files:
            md, _ = self.parseMMDFile(files["infos.txt"], asDict=True)
            row = []
            for name in ["Title", "Subtitle", "Serie", "Volume", "Genre", "License", "Author", "Email"]:
                row.append(QStandardItem(md.get(name, "")))
            self.mw.mdlFlatData.appendRow(row)
            return True
        return False 
    def loadsummary(self, files):
        if "summary.txt" in files:
            md, _ = self.parseMMDFile(files["summary.txt"], asDict=True)
            row = []
            for name in ["Situation", "Sentence", "Paragraph", "Page", "Full"]:
                row.append(QStandardItem(md.get(name, "")))
            self.mw.mdlFlatData.appendRow(row)
            return True
        else:
            return False
    @overload
    def parseMMDFile(self,text, asDict:Literal[False]=False)->tuple[list[tuple[str,str]], str]:...
    @overload
    def parseMMDFile(self,text, asDict:Literal[True]=True)->tuple[OrderedDict[str, str], str]:...
    def parseMMDFile(self,text:str, asDict=False)->tuple[list, str] | tuple[OrderedDict[str, str], str]:
        """
        Takes the content of a MultiMarkDown file (str) and returns:
        1. A list containing metadatas: (description, value) if asDict is False.
        If asDict is True, returns metadatas as an OrderedDict. Be aware that if multiple metadatas have the same description
        (which is stupid, but hey), they will be lost except the last one.
        2. The body of the file
        @param text: the content of the file
        @return: (list, str) or (OrderedDict, str)
        """
        md:list[tuple[str,str]] = []
        body = []
        descr = ""
        val = ""
        inBody = False
        for s in text.splitlines():
            if not inBody:
                m = re.match(r"^([^\s].*?):\s*(.*)$", s)
                if m:
                    # Commit last metadata
                    if descr:
                        if descr == "None":
                            descr = ""
                        md.append((descr, val))
                    descr = ""
                    val = ""
                    # Store new values
                    descr = m.group(1)
                    val = m.group(2)
                elif s[:4] == "    ":
                    val += "\n" + s.strip()
                elif s == "":
                    # End of metadatas
                    inBody = True
                    # Commit last metadata
                    if descr:
                        if descr == "None":
                            descr = ""
                        md.append((descr, val))
            else:
                body.append(s)

        # We remove the second empty line (since we save with two empty lines)
        if body and body[0] == "":
            body = body[1:]
        body = "\n".join(body)
        if not asDict:
            return md, body
        return OrderedDict(md), body

def loadProject(project:str,zip=None, tabLength:None|int=None):
    global currentProject
    currentProject=Project(project, tabLength, zip)
    return currentProject.loadProject()

def saveProject(zip:bool|None|Literal['None']='None'):
    global currentProject
    if currentProject.format!='0':
        return currentProject.saveProject()
    return currentProject.saveProject(zip)

class V0Project(Project):
    format='0'
    def saveProject(self, zip):
        """
        Saves the whole project. Call this function to save the project in Version 0 format.
        """
        mw = self.mainWindow()
        if not mw:
            return
        files:list[tuple[str, str|bytes]] = []
        files.append(("flatModel.xml", self.saveStandardItemModelXML(mw.mdlFlatData)))
        LOGGER.error("File format 0 does not save characters!")
        # files.append((saveStandardItemModelXML(mw.mdlCharacter), "perso.xml"))
        for mdl, filename in [(mw.mdlWorld, 'world'),(mw.mdlLabels, "labels"), (mw.mdlStatus, "status"), (mw.mdlPlots, "plots")]:
            self.saveStandardItemModelXML(mdl, filename+'.xml')
        files.append(("outline.xml",mw.mdlOutline.saveToXML()))
        files.append(("settings.pickle", settings.save(), ))
        # Does this not have a MANUSKRIPT file?
        self.savetozip(files, mw.currentProject or '')

    def saveFilesToZip(self,files, zipname):
        """Saves given files to zipname.
        files is actually a list of (content, filename)."""

        zf = zipfile.ZipFile(zipname, mode="w")

        for content, filename in files:
            zf.writestr(filename, content, compress_type=compression)
        zf.close()

    def saveStandardItemModelXML(self,mdl:QStandardItemModel, xml:str|None=None):
        """Saves the given QStandardItemModel to XML.
        If xml (filename) is given, saves to xml. Otherwise returns as string."""

        root = ET.Element("model")
        root.attrib["version"] = qApp.applicationVersion()

        # Header
        header = ET.SubElement(root, "header")
        vHeader = ET.SubElement(header, "vertical")
        for x in range(mdl.rowCount()):
            vH = ET.SubElement(vHeader, "label")
            vH.attrib["row"] = str(x)
            vH.attrib["text"] = str(mdl.headerData(x, Qt.Orientation.Vertical))

        hHeader = ET.SubElement(header, "horizontal")
        for y in range(mdl.columnCount()):
            hH = ET.SubElement(hHeader, "label")
            hH.attrib["row"] = str(y)
            hH.attrib["text"] = str(mdl.headerData(y, Qt.Orientation.Horizontal))

        # Data
        data = ET.SubElement(root, "data")
        self.saveItem(data, mdl)

        # LOGGER.info("Saving to {}.".format(xml))
        if xml:
            ET.ElementTree(root).write(xml, encoding="UTF-8", xml_declaration=True, pretty_print=True) # pyright: ignore[reportCallIssue]
        return ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)

    def saveItem(self,root, mdl, parent=QModelIndex()):
        for x in range(mdl.rowCount(parent)):
            row = ET.SubElement(root, "row")
            row.attrib["row"] = str(x)

            for y in range(mdl.columnCount(parent)):
                col = ET.SubElement(row, "col")
                col.attrib["col"] = str(y)
                if mdl.data(mdl.index(x, y, parent), Qt.ItemDataRole.DecorationRole) != None:
                    color = iconColor(mdl.data(mdl.index(x, y, parent), Qt.ItemDataRole.DecorationRole)).name(QColor.HexArgb)
                    col.attrib["color"] = color if color != "#ff000000" else "#00000000"
                if mdl.data(mdl.index(x, y, parent)) != "":
                    col.text = mdl.data(mdl.index(x, y, parent))
                if mdl.hasChildren(mdl.index(x, y, parent)):
                    self.saveItem(col, mdl, mdl.index(x, y, parent))

    ###########################################################################################
    # LOAD
    ###########################################################################################

    def loadProject(self,project):

        files = self.loadFilesFromZip(project)
        mw = mainWindow()

        errors = []

        if "flatModel.xml" in files:
            self.loadStandardItemModelXML(mw.mdlFlatData,
                                    files["flatModel.xml"], fromString=True)
        else:
            errors.append("flatModel.xml")

        if "perso.xml" in files:
            self.loadStandardItemModelXMLForCharacters(mw.mdlCharacter, files["perso.xml"])
        else:
            errors.append("perso.xml")

        if "world.xml" in files:
            self.loadStandardItemModelXML(mw.mdlWorld,
                                    files["world.xml"], fromString=True)
        else:
            errors.append("world.xml")

        if "labels.xml" in files:
            self.loadStandardItemModelXML(mw.mdlLabels,
                                    files["labels.xml"], fromString=True)
        else:
            errors.append("labels.xml")

        if "status.xml" in files:
            self.loadStandardItemModelXML(mw.mdlStatus,
                                    files["status.xml"], fromString=True)
        else:
            errors.append("status.xml")

        if "plots.xml" in files:
            self.loadStandardItemModelXML(mw.mdlPlots,
                                    files["plots.xml"], fromString=True)
        else:
            errors.append("plots.xml")

        if "outline.xml" in files:
            mw.mdlOutline.loadFromXML(files["outline.xml"], fromString=True)
        else:
            errors.append("outline.xml")

        if "settings.txt" in files:
            settings.load(files["settings.txt"], fromString=True, protocol=0)
        else:
            errors.append("settings.txt")

        if "settings.pickle" in files:
            LOGGER.info("Pickle settings files are no longer supported for security reasons. You can delete it from your data.")

        return errors

    def loadStandardItemModelXML(self,mdl, xml, fromString=False):
        """Load data to a QStandardItemModel mdl from xml.
        By default xml is a filename. If fromString=True, xml is a string containing the data."""

        # LOGGER.info("Loading {}...".format(xml))

        if not fromString:
            try:
                tree = ET.parse(xml)
            except Exception:
                LOGGER.error("Failed to load XML for QStandardItemModel (%s).", xml)
                return
        else:
            root = ET.fromstring(xml)

        # root = tree.getroot()

        # Header
        hLabels = []
        vLabels = []
        if header:=root.find("header"):
            if hor:=header.find('horizontal'):
                hLabels.extend(map(lambda e:e.attrib["text"], hor.findall('label')))
            else:
                LOGGER.debug('No horizontal labels')
            if ver:=header.find("vertical"):
                vLabels.extend(map(lambda e:e.attrib["text"], ver.findall('label')))
            else:
                LOGGER.debug('No vertical labels')
        else:
            LOGGER.debug('No header was found')
            


        # LOGGER.debug(root.find("header").find("vertical").text)

        # mdl.setVerticalHeaderLabels(vLabels)
        # mdl.setHorizontalHeaderLabels(hLabels)

        # Populates with empty items
        for i in enumerate(vLabels):
            row = []
            for r in enumerate(hLabels):
                row.append(QStandardItem())
            mdl.appendRow(row)
        # Data
        data = root.find("data")
        self.loadItem(data, mdl)

        return True

    def loadItem(self,root, mdl, parent=QModelIndex()):
        for row in root:
            r = int(row.attrib["row"])
            for col in row:
                c = int(col.attrib["col"])
                item = mdl.itemFromIndex(mdl.index(r, c, parent))
                if not item:
                    item = QStandardItem()
                    mdl.itemFromIndex(parent).setChild(r, c, item)

                if col.text:
                    # mdl.setData(mdl.index(r, c, parent), col.text)
                    item.setText(col.text)

                if "color" in col.attrib:
                    # mdl.itemFromIndex(mdl.index(r, c, parent)).setIcon(iconFromColorString(col.attrib["color"]))
                    item.setIcon(iconFromColorString(col.attrib["color"]))

                if len(col) != 0:
                    # loadItem(col, mdl, mdl.index(r, c, parent))
                    self.loadItem(col, mdl, mdl.indexFromItem(item))


    def loadStandardItemModelXMLForCharacters(self,mdl, xml):
        """
        Loads a standardItemModel saved to XML by version 0, but for the new characterModel.
        @param mdl: characterModel
        @param xml: the content of the xml
        @return: nothing
        """
        mdl = mainWindow().mdlCharacter
        root = ET.fromstring(xml)
        data = root.find("data")
        if data is None:
            return

        for row in data:
            char = Character(mdl)

            for col in row:
                c = int(col.attrib["col"])

                # Value
                if col.text:
                    char._data[c] = col.text

                # Color
                if "color" in col.attrib:
                    char.setColor(QColor(col.attrib["color"]))
                    
                # Infos
                if len(col) != 0:
                    for rrow in col:
                        info = CharacterInfo(char)
                        for ccol in rrow:
                            cc = int(ccol.attrib["col"])
                            if cc == 11 and ccol.text:
                                info.description = ccol.text
                            if cc == 12 and ccol.text:
                                info.value = ccol.text
                        char.infos.append(info)

            mdl.characters.append(char)
