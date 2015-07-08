#!/usr/bin/env python
#--!-- coding: utf8 --!--
 
from qt import *
from enums import *
from functions import *
import re

###############################################################################
# SHORT REFERENCES
###############################################################################

# A regex used to match references
RegEx = r"{(\w):(\d+):?.*?}"
# A non-capturing regex used to identify references
RegExNonCapturing = r"{\w:\d+:?.*?}"
# The basic format of the references
EmptyRef = "{{{}:{}:{}}}"
PersoLetter = "C"
TextLetter = "T"
PlotLetter = "P"
WorldLetter = "W"

def plotReference(ID):
    "Takes the ID of a plot and returns a reference for that plot."
    return EmptyRef.format(PlotLetter, ID, "")

def persoReference(ID):
    "Takes the ID of a character and returns a reference for that character."
    return EmptyRef.format(PersoLetter, ID, "")

def textReference(ID):
    "Takes the ID of an outline item and returns a reference for that item."
    return EmptyRef.format(TextLetter, ID, "")

def worldReference(ID):
    "Takes the ID of a world item and returns a reference for that item."
    return EmptyRef.format(WordLetter, ID, "")

###############################################################################
# READABLE INFOS
###############################################################################

def infos(ref):
    """Returns a full paragraph in HTML format 
    containing detailed infos about the reference ``ref``.
    """
    match = re.fullmatch(RegEx, ref)
    if not match:
        return qApp.translate("references", "Not a reference: {}.").format(ref)
    
    _type = match.group(1)
    _ref = match.group(2)
    
    # A text or outine item
    if _type == TextLetter:
        m = mainWindow().mdlOutline
        idx = m.getIndexByID(_ref)
        
        if not idx.isValid():
            return qApp.translate("references", "Unknown reference: {}.").format(ref)
        
        item = idx.internalPointer()
        
        #Titles
        pathTitle = qApp.translate("references", "Path:")
        statsTitle = qApp.translate("references", "Stats:")
        POVTitle = qApp.translate("references", "POV:")
        statusTitle = qApp.translate("references", "Status:")
        labelTitle = qApp.translate("references", "Label:")
        ssTitle = qApp.translate("references", "Short summary:")
        lsTitle = qApp.translate("references", "Long summary:")
        notesTitle = qApp.translate("references", "Notes:")
        
        # The POV of the scene
        POV = ""
        if item.POV():
            POV = "<a href='{ref}'>{text}</a>".format(
                ref=persoReference(item.POV()),
                text=mainWindow().mdlPersos.getPersoNameByID(item.POV()))
        
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
        ss = item.data(Outline.summarySentance.value)
        ls = item.data(Outline.summaryFull.value)
        notes = item.data(Outline.notes.value)
        
        text = """<h1>{title}</h1>
        <p><b>{pathTitle}</b> {path}</p>
        <p><b>{statsTitle}</b> {stats}<br>
            {POV}
            {status}
            {label}</p>
        {ss}
        {ls}
        {notes}
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
                ss=ss.replace("\n", "<br>")) if ss else "",
            ls="<p><b>{lsTitle}</b><br>{ls}</p>".format(
                lsTitle=lsTitle,
                ls=ls.replace("\n", "<br>")) if ls else "",
            notes="<p><b>{notesTitle}</b><br>{notes}</p>".format(
                notesTitle=notesTitle,
                notes=linkifyAllRefs(basicT2TFormat(notes))) if notes else "",
            )
        
        return text
    
    # A character
    elif _type == PersoLetter:
        m = mainWindow().mdlPersos
        index = m.getIndexFromID(_ref)
        name = m.name(index.row())
        
        # Titles
        basicTitle = qApp.translate("references", "Basic infos")
        detailedTitle = qApp.translate("references", "Detailed infos")
        POVof = qApp.translate("references", "POV of:")
        referencedIn = qApp.translate("references", "Referenced in:")
        
        # Goto (link)
        goto = qApp.translate("references", "Go to {}.")
        goto = goto.format(refToLink(ref))
        
        # basic infos
        basic = []
        for i in [
            (Perso.motivation,  qApp.translate("references", "Motivation"),     False),
            (Perso.goal,                qApp.translate("references", "Goal"),           False),
            (Perso.conflict,    qApp.translate("references", "Conflict"),       False),
            (Perso.epiphany,    qApp.translate("references", "Epiphany"),       False),
            (Perso.summarySentance,     qApp.translate("references", "Short summary"),  True),
            (Perso.summaryPara, qApp.translate("references", "Longer summary"), True),
            ]:
            val = m.data(index.sibling(index.row(), i[0].value))
            if val:
                basic .append("<b>{title}:</b>{n}{val}".format(
                    title=i[1],
                    n = "\n" if i[2] else " ",
                    val=val))
        basic = "<br>".join(basic)
        
        # detailed infos
        detailed = []
        for _name, _val in m.listPersoInfos(index):
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
                text=oM.data(idx, Outline.title.value))
        
        # List scenes where character is referenced
        listRefs = listReferences(ref, referencedIn)
        
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
            references=listRefs if listRefs else "",
                )
        return text
    
    # A plot
    elif _type == PlotLetter:
        m = mainWindow().mdlPlots
        index = m.getIndexFromID(_ref)
        name = m.getPlotNameByID(_ref)
        
        # Titles
        descriptionTitle = qApp.translate("references", "Description")
        resultTitle = qApp.translate("references", "Result")
        charactersTitle = qApp.translate("references", "Characters")
        stepsTitle = qApp.translate("references", "Resolution steps")
        referenceTitle = qApp.translate("references", "Referenced in:")
        
        # Goto (link)
        goto = qApp.translate("references", "Go to {}.")
        goto = goto.format(refToLink(ref))
        
        # Description
        description = m.data(index.sibling(index.row(), 
                                           Plot.description.value))
        
        # Result
        result =  m.data(index.sibling(index.row(), 
                                       Plot.result.value))
            
        # Characters
        pM = mainWindow().mdlPersos
        item = m.item(index.row(), Plot.persos.value)
        characters = ""
        if item:
            for r in range(item.rowCount()):
                ID = item.child(r, 0).text()
                characters += "<li><a href='{link}'>{text}</a>".format(
                    link=persoReference(ID),
                    text=pM.getPersoNameByID(ID))
                
        # Resolution steps
        steps = ""
        item = m.item(index.row(), Plot.subplots.value)
        if item:
            for r in range(item.rowCount()):
                title = item.child(r, Subplot.name.value).text()
                summary = item.child(r, Subplot.summary.value).text()
                meta = item.child(r, Subplot.meta.value).text()
                if meta:
                    meta = " <span style='color:gray;'>({})</span>".format(meta)
                steps += "<li><b>{title}</b>{summary}{meta}</li>".format(
                    title=title,
                    summary=": {}".format(summary) if summary else "",
                    meta = meta if meta else "")
        
        # List scenes where item is referenced
        references = listReferences(ref, referenceTitle)
        
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
            references=references
                )
        return text
    
    # A World item
    elif _type == WorldLetter:
        m = mainWindow().mdlWorld
        index = m.indexByID(_ref)
        name = m.name(index)
        
        # Titles
        descriptionTitle = qApp.translate("references", "Description")
        passionTitle = qApp.translate("references", "Passion")
        conflictTitle = qApp.translate("references", "Conflict")
        referenceTitle = qApp.translate("references", "Referenced in:")
        
        # Goto (link)
        goto = qApp.translate("references", "Go to {}.")
        goto = goto.format(refToLink(ref))
        
        # Description
        description = basicFormat(m.description(index))
        
        # Passion
        passion =  basicFormat(m.passion(index))
        
        # Conflict
        conflict =  basicFormat(m.conflict(index))
        
        # List scenes where item is referenced
        references = listReferences(ref, referenceTitle)
        
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
            references=references
            )
        return text
    
    else:
        return qApp.translate("references", "Unknown reference: {}.").format(ref)
    
def tooltip(ref):
    "Returns a tooltip in HTML for the reference ``ref``."
    match = re.fullmatch(RegEx, ref)
    
    if not match:
        return qApp.translate("references", "Not a reference: {}.").format(ref)
    
    _type = match.group(1)
    _ref = match.group(2)
    
    if _type == TextLetter:
        m = mainWindow().mdlOutline
        idx = m.getIndexByID(_ref)
        
        if not idx.isValid():
            return qApp.translate("references", "Unknown reference: {}.").format(ref)
        
        item = idx.internalPointer()
        
        tooltip = qApp.translate("references", "Text: <b>{}</b>").format(item.title())
        tooltip += "<br><i>{}</i>".format(item.path())
        
        return tooltip
    
    elif _type == PersoLetter:
        m = mainWindow().mdlPersos
        name = m.item(int(_ref), Perso.name.value).text()
        return qApp.translate("references", "Character: <b>{}</b>").format(name)
            
    elif _type == PlotLetter:
        m = mainWindow().mdlPlots
        name = m.getPlotNameByID(_ref)
        return qApp.translate("references", "Plot: <b>{}</b>").format(name)
    
    elif _type == WorldLetter:
        m = mainWindow().mdlWorld
        item = m.itemByID(_ref)
        if item:
            name = item.text()
            path = m.path(item)
            return qApp.translate("references", "World: <b>{name}</b>{path}").format(
                name=name,
                path=" <span style='color:gray;'>({})</span>".format(path) if path else "")
    
    return qApp.translate("references", "Unknown reference: {}.").format(ref)
    
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
            
        elif _type == PersoLetter:
            m = mainWindow().mdlPersos
            text = m.item(int(_ref), Perso.name.value).text()
            
        elif _type == PlotLetter:
            m = mainWindow().mdlPlots
            text = m.getPlotNameByID(_ref)
            
        elif _type == WorldLetter:
            m = mainWindow().mdlWorld
            text = m.itemByID(_ref).text()
            
        if text:
            return "<a href='{ref}'>{text}</a>".format(
                    ref=ref,
                    text=text)
        else:
            return ref
    
def linkifyAllRefs(text):
    "Takes all the references in ``text`` and transform them into HMTL links."
    return re.sub(RegEx, lambda m: refToLink(m.group(0)), text)
    
def listReferences(ref, title):
    oM = mainWindow().mdlOutline
    listRefs = ""
    ref = ref[:ref.index(":", ref.index(":") + 1)]
    lst = oM.findItemsContaining(ref, [Outline.notes.value])
    for t in lst:
        idx = oM.getIndexByID(t)
        listRefs += "<li><a href='{link}'>{text}</a></li>".format(
            link=textReference(t),
            text=oM.data(idx, Outline.title.value))
        
    return "<h2>{title}</h2><ul>{ref}</ul>".format(
                title=title,
                ref=listRefs) if listRefs else ""
    
def basicT2TFormat(text, formatting=True, EOL=True, titles=True):
    "A very basic t2t formatter to display notes and texts."
    text = text.splitlines()
    for n, line in enumerate(text):
        if formatting:
            line = re.sub("\*\*(.*?)\*\*", "<b>\\1</b>", line)
            line = re.sub("//(.*?)//", "<i>\\1</i>", line)
            line = re.sub("__(.*?)__", "<u>\\1</u>", line)
            
        if titles:
            for i in range(1, 6):
                r1 = '^\s*{s}([^=].*[^=]){s}\s*$'.format(s="=" * i)
                r2 = '^\s*{s}([^\+].*[^\+]){s}\s*$'.format(s="\\+" * i)
                t = "<h{n}>\\1</h{n}>".format(n=i)
                line = re.sub(r1, t, line)
                line = re.sub(r2, t, line)
        text[n] = line
    text = "\n".join(text)
    if EOL:
        text = text.replace("\n", "<br>")
            
    return text

def basicFormat(text):
    if not text:
        return ""
    text = text.replace("\n", "<br>")
    text = linkifyAllRefs(text)
    return text

def open(ref):
    "Identify ``ref`` and open it."
    match = re.fullmatch(RegEx, ref)
    if not match:
        return
    
    _type = match.group(1)
    _ref = match.group(2)
    
    if _type == PersoLetter:
        mw = mainWindow()
        item = mw.lstPersos.getItemByID(_ref)
        
        if item:
            mw.tabMain.setCurrentIndex(2)
            mw.lstPersos.setCurrentItem(item)
            return True
            
        print("Ref not found")
        return False
    
    elif _type == TextLetter:
        mw = mainWindow()
        index = mw.mdlOutline.getIndexByID(_ref)
        
        if index.isValid():
            mw.tabMain.setCurrentIndex(6)
            mw.mainEditor.setCurrentModelIndex(index, newTab=True)
            return True
        else:
            print("Ref not found")
            return False
    
    elif  _type == PlotLetter:
        mw = mainWindow()
        item = mw.lstPlots.getItemByID(_ref)
        
        if item:
            mw.tabMain.setCurrentIndex(3)
            mw.lstPlots.setCurrentItem(item)
            return True
        
        print("Ref not found")
        return False
    
    elif  _type == WorldLetter:
        mw = mainWindow()
        item = mw.mdlWorld.itemByID(_ref)
        
        if item:
            mw.tabMain.setCurrentIndex(4)
            mw.treeWorld.setCurrentIndex(
                mw.mdlWorld.indexFromItem(item))
            return True
        
        print("Ref not found")
        return False
    
    print("Ref not implemented")
    return False