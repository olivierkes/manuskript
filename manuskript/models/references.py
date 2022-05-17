#!/usr/bin/env python
# --!-- coding: utf8 --!--

import re

import logging
LOGGER = logging.getLogger(__name__)

###############################################################################
# SHORT REFERENCES
###############################################################################

# A regex used to match references
from PyQt5.QtWidgets import qApp
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from manuskript.enums import Outline
from manuskript.enums import Character
from manuskript.enums import Plot
from manuskript.enums import PlotStep
from manuskript.functions import mainWindow, mixColors, safeTranslate
from manuskript.ui import style as S


RegEx = r"{(\w):(\d+):?.*?}"
# A non-capturing regex used to identify references
RegExNonCapturing = r"{\w:\d+:?.*?}"
# The basic format of the references
EmptyRef = "{{{}:{}:{}}}"
EmptyRefSearchable = "{{{}:{}:"
CharacterLetter = "C"
TextLetter = "T"
PlotLetter = "P"
WorldLetter = "W"

# Colors
TextHighlightColor = QColor(mixColors(QColor(Qt.blue).name(), S.window, .3))
CharacterHighlightColor = QColor(mixColors(QColor(Qt.yellow).name(), S.window, .3))
PlotHighlightColor = QColor(mixColors(QColor(Qt.red).name(), S.window, .3))
WorldHighlightColor = QColor(mixColors(QColor(Qt.green).name(), S.window, .3))


def plotReference(ID, searchable=False):
    """Takes the ID of a plot and returns a reference for that plot.
    @searchable: returns a stripped version that allows simple text search."""
    if not searchable:
        return EmptyRef.format(PlotLetter, ID, "")
    else:
        return EmptyRefSearchable.format(PlotLetter, ID, "")


def characterReference(ID, searchable=False):
    """Takes the ID of a character and returns a reference for that character.
    @searchable: returns a stripped version that allows simple text search."""
    if not searchable:
        return EmptyRef.format(CharacterLetter, ID, "")
    else:
        return EmptyRefSearchable.format(CharacterLetter, ID, "")


def textReference(ID, searchable=False):
    """Takes the ID of an outline item and returns a reference for that item.
    @searchable: returns a stripped version that allows simple text search."""
    if not searchable:
        return EmptyRef.format(TextLetter, ID, "")
    else:
        return EmptyRefSearchable.format(TextLetter, ID, "")


def worldReference(ID, searchable=False):
    """Takes the ID of a world item and returns a reference for that item.
    @searchable: returns a stripped version that allows simple text search."""
    if not searchable:
        return EmptyRef.format(WorldLetter, ID, "")
    else:
        return EmptyRefSearchable.format(WorldLetter, ID, "")


###############################################################################
# READABLE INFOS
###############################################################################

def infos(ref):
    """Returns a full paragraph in HTML format
    containing detailed infos about the reference ``ref``.
    """
    match = re.fullmatch(RegEx, ref)
    if not match:
        return safeTranslate(qApp, "references", "Not a reference: {}.").format(ref)

    _type = match.group(1)
    _ref = match.group(2)

    # A text or outline item
    if _type == TextLetter:
        m = mainWindow().mdlOutline
        idx = m.getIndexByID(_ref)

        if not idx.isValid():
            return safeTranslate(qApp, "references", "Unknown reference: {}.").format(ref)

        item = idx.internalPointer()

        # Titles
        pathTitle = safeTranslate(qApp, "references", "Path:")
        statsTitle = safeTranslate(qApp, "references", "Stats:")
        POVTitle = safeTranslate(qApp, "references", "POV:")
        statusTitle = safeTranslate(qApp, "references", "Status:")
        labelTitle = safeTranslate(qApp, "references", "Label:")
        ssTitle = safeTranslate(qApp, "references", "Short summary:")
        lsTitle = safeTranslate(qApp, "references", "Long summary:")
        notesTitle = safeTranslate(qApp, "references", "Notes:")

        # The POV of the scene
        POV = ""
        if item.POV():
            POV = "<a href='{ref}'>{text}</a>".format(
                    ref=characterReference(item.POV()),
                    text=mainWindow().mdlCharacter.getCharacterByID(item.POV()).name())

        # The status of the scene
        status = item.status()
        if status:
            status = mainWindow().mdlStatus.item(int(status), 0).text()
        else:
            status = ""

        # The label of the scene
        label = item.label()
        if label:
            label = mainWindow().mdlLabels.item(int(label), 0).text()
        else:
            label = ""

        # The path of the scene
        path = item.pathID()
        pathStr = []
        for _id, title in path:
            pathStr.append("<a href='{ref}'>{text}</a>".format(
                    ref=textReference(_id),
                    text=title))
        path = " > ".join(pathStr)

        # Summaries and notes
        ss = item.data(Outline.summarySentence)
        ls = item.data(Outline.summaryFull)
        notes = item.data(Outline.notes)

        text = """<h1>{title}</h1>
        <p><b>{pathTitle}</b> {path}</p>
        <p><b>{statsTitle}</b> {stats}<br>
            {POV}
            {status}
            {label}</p>
        {ss}
        {ls}
        {notes}
        {references}
        """.format(
                title=item.title(),
                pathTitle=pathTitle,
                path=path,
                statsTitle=statsTitle,
                stats=item.stats(),
                POV="<b>{POVTitle}</b> {POV}<br>".format(
                        POVTitle=POVTitle,
                        POV=POV) if POV else "",
                status="<b>{statusTitle}</b> {status}<br>".format(
                        statusTitle=statusTitle,
                        status=status) if status else "",
                label="<b>{labelTitle}</b> {label}</p>".format(
                        labelTitle=labelTitle,
                        label=label) if label else "",
                ss="<p><b>{ssTitle}</b> {ss}</p>".format(
                        ssTitle=ssTitle,
                        ss=ss.replace("\n", "<br>")) if ss.strip() else "",
                ls="<p><b>{lsTitle}</b><br>{ls}</p>".format(
                        lsTitle=lsTitle,
                        ls=ls.replace("\n", "<br>")) if ls.strip() else "",
                notes="<p><b>{notesTitle}</b><br>{notes}</p>".format(
                        notesTitle=notesTitle,
                        notes=linkifyAllRefs(notes)) if notes.strip() else "",
                references=listReferences(ref)
        )

        return text

    # A character
    elif _type == CharacterLetter:
        m = mainWindow().mdlCharacter
        c = m.getCharacterByID(int(_ref))
        if c == None:
            return safeTranslate(qApp, "references", "Unknown reference: {}.").format(ref)

        index = c.index()

        name = c.name()

        # Titles
        basicTitle = safeTranslate(qApp, "references", "Basic info")
        detailedTitle = safeTranslate(qApp, "references", "Detailed info")
        POVof = safeTranslate(qApp, "references", "POV of:")

        # Goto (link)
        goto = safeTranslate(qApp, "references", "Go to {}.")
        goto = goto.format(refToLink(ref))

        # basic infos
        basic = []
        for i in [
            (Character.motivation, safeTranslate(qApp, "references", "Motivation"), False),
            (Character.goal, safeTranslate(qApp, "references", "Goal"), False),
            (Character.conflict, safeTranslate(qApp, "references", "Conflict"), False),
            (Character.epiphany, safeTranslate(qApp, "references", "Epiphany"), False),
            (Character.summarySentence, safeTranslate(qApp, "references", "Short summary"), True),
            (Character.summaryPara, safeTranslate(qApp, "references", "Longer summary"), True),
        ]:

            val = m.data(index.sibling(index.row(), i[0].value))

            if val:
                basic.append("<b>{title}:</b>{n}{val}".format(
                        title=i[1],
                        n="\n" if i[2] else " ",
                        val=val))
        basic = "<br>".join(basic)

        # detailed infos
        detailed = []
        for _name, _val in c.listInfos():
            detailed.append("<b>{}:</b> {}".format(
                    _name,
                    _val))
        detailed = "<br>".join(detailed)

        # list scenes of which it is POV
        oM = mainWindow().mdlOutline
        lst = oM.findItemsByPOV(_ref)

        listPOV = ""
        for t in lst:
            idx = oM.getIndexByID(t)
            listPOV += "<li><a href='{link}'>{text}</a></li>".format(
                    link=textReference(t),
                    text=oM.data(idx, Outline.title))

        text = """<h1>{name}</h1>
        {goto}
        {basicInfos}
        {detailedInfos}
        {POV}
        {references}
        """.format(
                name=name,
                goto=goto,
                basicInfos="<h2>{basicTitle}</h2>{basic}".format(
                        basicTitle=basicTitle,
                        basic=basic) if basic else "",
                detailedInfos="<h2>{detailedTitle}</h2>{detailed}".format(
                        detailedTitle=detailedTitle,
                        detailed=detailed) if detailed else "",
                POV="<h2>{POVof}</h2><ul>{listPOV}</ul>".format(
                        POVof=POVof,
                        listPOV=listPOV) if listPOV else "",
                references=listReferences(ref)
        )
        return text

    # A plot
    elif _type == PlotLetter:
        m = mainWindow().mdlPlots
        index = m.getIndexFromID(_ref)
        name = m.getPlotNameByID(_ref)

        if not index.isValid():
            return safeTranslate(qApp, "references", "Unknown reference: {}.").format(ref)

        # Titles
        descriptionTitle = safeTranslate(qApp, "references", "Description")
        resultTitle = safeTranslate(qApp, "references", "Result")
        charactersTitle = safeTranslate(qApp, "references", "Characters")
        stepsTitle = safeTranslate(qApp, "references", "Resolution steps")

        # Goto (link)
        goto = safeTranslate(qApp, "references", "Go to {}.")
        goto = goto.format(refToLink(ref))

        # Description
        description = m.data(index.sibling(index.row(),
                                           Plot.description))

        # Result
        result = m.data(index.sibling(index.row(),
                                      Plot.result))

        # Characters
        pM = mainWindow().mdlCharacter
        item = m.item(index.row(), Plot.characters)
        characters = ""
        if item:
            for r in range(item.rowCount()):
                ID = item.child(r, 0).text()
                characters += "<li><a href='{link}'>{text}</a>".format(
                        link=characterReference(ID),
                        text=pM.getCharacterByID(ID).name())

        # Resolution steps
        steps = ""
        item = m.item(index.row(), Plot.steps)
        if item:
            for r in range(item.rowCount()):
                title = item.child(r, PlotStep.name).text()
                summary = item.child(r, PlotStep.summary).text()
                meta = item.child(r, PlotStep.meta).text()
                if meta:
                    meta = " <span style='color:gray;'>({})</span>".format(meta)
                steps += "<li><b>{title}</b>{summary}{meta}</li>".format(
                        title=title,
                        summary=": {}".format(summary) if summary else "",
                        meta=meta if meta else "")

        text = """<h1>{name}</h1>
        {goto}
        {characters}
        {description}
        {result}
        {steps}
        {references}
        """.format(
                name=name,
                goto=goto,
                description="<h2>{title}</h2>{text}".format(
                        title=descriptionTitle,
                        text=description) if description else "",
                result="<h2>{title}</h2>{text}".format(
                        title=resultTitle,
                        text=result) if result else "",
                characters="<h2>{title}</h2><ul>{lst}</ul>".format(
                        title=charactersTitle,
                        lst=characters) if characters else "",
                steps="<h2>{title}</h2><ul>{steps}</ul>".format(
                        title=stepsTitle,
                        steps=steps) if steps else "",
                references=listReferences(ref)
        )
        return text

    # A World item
    elif _type == WorldLetter:
        m = mainWindow().mdlWorld
        index = m.indexByID(_ref)
        name = m.name(index)

        if not index.isValid():
            return safeTranslate(qApp, "references", "Unknown reference: {}.").format(ref)

        # Titles
        descriptionTitle = safeTranslate(qApp, "references", "Description")
        passionTitle = safeTranslate(qApp, "references", "Passion")
        conflictTitle = safeTranslate(qApp, "references", "Conflict")

        # Goto (link)
        goto = safeTranslate(qApp, "references", "Go to {}.")
        goto = goto.format(refToLink(ref))

        # Description
        description = basicFormat(m.description(index))

        # Passion
        passion = basicFormat(m.passion(index))

        # Conflict
        conflict = basicFormat(m.conflict(index))

        text = """<h1>{name}</h1>
        {goto}
        {description}
        {passion}
        {conflict}
        {references}
        """.format(
                name=name,
                goto=goto,
                description="<h2>{title}</h2>{text}".format(
                        title=descriptionTitle,
                        text=description) if description else "",
                passion="<h2>{title}</h2>{text}".format(
                        title=passionTitle,
                        text=passion) if passion else "",
                conflict="<h2>{title}</h2><ul>{lst}</ul>".format(
                        title=conflictTitle,
                        lst=conflict) if conflict else "",
                references=listReferences(ref)
        )
        return text

    else:
        return safeTranslate(qApp, "references", "Unknown reference: {}.").format(ref)


def shortInfos(ref):
    """Returns infos about reference ``ref``.
    Returns -1 if ``ref`` is not a valid reference, and None if it is valid but unknown."""
    match = re.fullmatch(RegEx, ref)

    if not match:
        return -1

    _type = match.group(1)
    _ref = match.group(2)

    infos = {}
    infos["ID"] = _ref

    if _type == TextLetter:

        infos["type"] = TextLetter

        m = mainWindow().mdlOutline
        idx = m.getIndexByID(_ref)

        if not idx.isValid():
            return None

        item = idx.internalPointer()

        if item.isFolder():
            infos["text_type"] = "folder"
        else:
            infos["text_type"] = "text"

        infos["title"] = item.title()
        infos["path"] = item.path()
        return infos

    elif _type == CharacterLetter:

        infos["type"] = CharacterLetter

        m = mainWindow().mdlCharacter
        c = m.getCharacterByID(_ref)

        if c:
            infos["title"] = c.name()
            infos["name"] = c.name()
            return infos

    elif _type == PlotLetter:

        infos["type"] = PlotLetter

        m = mainWindow().mdlPlots
        name = m.getPlotNameByID(_ref)
        if name:
            infos["title"] = name
            return infos

    elif _type == WorldLetter:

        infos["type"] = WorldLetter

        m = mainWindow().mdlWorld
        item = m.itemByID(_ref)
        if item:
            name = item.text()
            path = m.path(item)
            infos["title"] = name
            infos["path"] = path
            return infos

    return None


def title(ref):
    """Returns a the title (or name) for the reference ``ref``."""
    infos = shortInfos(ref)
    if infos and infos != -1 and "title" in infos:
        return infos["title"]
    else:
        return None

def type(ref):
    infos = shortInfos(ref)
    if infos and infos != -1:
        return infos["type"]

def ID(ref):
    infos = shortInfos(ref)
    if infos and infos != -1:
        return infos["ID"]

def tooltip(ref):
    """Returns a tooltip in HTML for the reference ``ref``."""
    infos = shortInfos(ref)

    if not infos:
        return safeTranslate(qApp, "references", "<b>Unknown reference:</b> {}.").format(ref)

    if infos == -1:
        return safeTranslate(qApp, "references", "Not a reference: {}.").format(ref)


    if infos["type"] == TextLetter:
        if infos["text_type"] == "folder":
            tt = safeTranslate(qApp, "references", "Folder: <b>{}</b>").format(infos["title"])
        else:
            tt = safeTranslate(qApp, "references", "Text: <b>{}</b>").format(infos["title"])
        tt += "<br><i>{}</i>".format(infos["path"])
        return tt

    elif infos["type"] == CharacterLetter:
        return safeTranslate(qApp, "references", "Character: <b>{}</b>").format(infos["title"])

    elif infos["type"] == PlotLetter:
        return safeTranslate(qApp, "references", "Plot: <b>{}</b>").format(infos["title"])

    elif infos["type"] == WorldLetter:
        return safeTranslate(qApp, "references", "World: <b>{name}</b>{path}").format(
                    name=infos["title"],
                    path=" <span style='color:gray;'>({})</span>".format(infos["path"]) if infos["path"] else "")


###############################################################################
# FUNCTIONS
###############################################################################

def refToLink(ref):
    """Transforms the reference ``ref`` in a link displaying useful infos
    about that reference. For character, character's name. For text item,
    item's name, etc.
    """
    match = re.fullmatch(RegEx, ref)
    if match:
        _type = match.group(1)
        _ref = match.group(2)
        text = ""
        if _type == TextLetter:
            m = mainWindow().mdlOutline
            idx = m.getIndexByID(_ref)
            if idx.isValid():
                item = idx.internalPointer()
                text = item.title()

        elif _type == CharacterLetter:
            m = mainWindow().mdlCharacter
            c = m.getCharacterByID(int(_ref))
            if c:
                text = c.name()

        elif _type == PlotLetter:
            m = mainWindow().mdlPlots
            text = m.getPlotNameByID(_ref)

        elif _type == WorldLetter:
            m = mainWindow().mdlWorld
            item = m.itemByID(_ref)
            if item:
                text = item.text()

        if text:
            return "<a href='{ref}'>{text}</a>".format(
                    ref=ref,
                    text=text)
        else:
            return ref

def linkifyAllRefs(text):
    """Takes all the references in ``text`` and transform them into HMTL links."""
    return re.sub(RegEx, lambda m: refToLink(m.group(0)), text)

def findReferencesTo(ref, parent=None, recursive=True):
    """List of text items containing references ref, and returns IDs.
    Starts from item parent. If None, starts from root."""
    oM = mainWindow().mdlOutline

    if parent == None:
        parent = oM.rootItem

    # Removes everything after the second ':': '{L:ID:random text}' → '{L:ID:'
    ref = ref[:ref.index(":", ref.index(":") + 1)+1]

    # Bare form '{L:ID}'
    ref2 = ref[:-1] + "}"

    # Since it's a simple search (no regex), we search for both.
    lst = parent.findItemsContaining(ref, [Outline.notes], recursive=recursive)
    lst += parent.findItemsContaining(ref2, [Outline.notes], recursive=recursive)

    return lst

def listReferences(ref, title=safeTranslate(qApp, "references", "Referenced in:")):
    oM = mainWindow().mdlOutline
    listRefs = ""

    lst = findReferencesTo(ref)

    for t in lst:
        idx = oM.getIndexByID(t)
        listRefs += "<li><a href='{link}'>{text}</a></li>".format(
                link=textReference(t),
                text=oM.data(idx, Outline.title))

    return "<h2>{title}</h2><ul>{ref}</ul>".format(
            title=title,
            ref=listRefs) if listRefs else ""

def basicFormat(text):
    if not text:
        return ""
    text = text.replace("\n", "<br>")
    text = linkifyAllRefs(text)
    return text

def open(ref):
    """Identify ``ref`` and open it."""
    match = re.fullmatch(RegEx, ref)
    if not match:
        return

    _type = match.group(1)
    _ref = match.group(2)

    if _type == CharacterLetter:
        mw = mainWindow()
        item = mw.lstCharacters.getItemByID(_ref)

        if item:
            mw.tabMain.setCurrentIndex(mw.TabPersos)
            mw.lstCharacters.setCurrentItem(item)
            return True

        LOGGER.error("Character reference {} not found.".format(ref))
        return False

    elif _type == TextLetter:
        mw = mainWindow()
        index = mw.mdlOutline.getIndexByID(_ref)

        if index.isValid():
            mw.tabMain.setCurrentIndex(mw.TabRedac)
            mw.mainEditor.setCurrentModelIndex(index, newTab=True)
            return True
        else:
            LOGGER.error("Text reference {} not found.".format(ref))
            return False

    elif _type == PlotLetter:
        mw = mainWindow()
        item = mw.lstPlots.getItemByID(_ref)

        if item:
            mw.tabMain.setCurrentIndex(mw.TabPlots)
            mw.lstPlots.setCurrentItem(item)
            return True

        LOGGER.error("Plot reference {} not found.".format(ref))
        return False

    elif _type == WorldLetter:
        mw = mainWindow()
        item = mw.mdlWorld.itemByID(_ref)

        if item:
            mw.tabMain.setCurrentIndex(mw.TabWorld)
            mw.treeWorld.setCurrentIndex(
                    mw.mdlWorld.indexFromItem(item))
            return True

        LOGGER.error("World reference {} not found.".format(ref))
        return False

    LOGGER.error("Unable to identify reference type: {}.".format(ref))
    return False
