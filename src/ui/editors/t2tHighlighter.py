#!/usr/bin/python
# -*- coding: utf8 -*-

from qt import *
from ui.editors.t2tFunctions import *
from ui.editors.blockUserData import blockUserData
from ui.editors.t2tHighlighterStyle import t2tHighlighterStyle
import re

# This is aiming at implementing every rule from www.txt2tags.org/rules.html
# But we're not there yet.

#FIXME: macro words not hilighted properly if at the begining of a line.

#TODO: parse %!postproc et !%preproc, et si la ligne se termine par une couleur en commentaire (%#FF00FF), utiliser cette couleur pour highlighter. Permet des règles customisées par document, facilement.


class t2tHighlighter (QSyntaxHighlighter):
    """Syntax highlighter for the Txt2Tags language.
    """

    def __init__(self, editor, style="Default"):
        QSyntaxHighlighter.__init__(self, editor.document())

        self.editor = editor

        # Stupid variable that fixes the loss of QTextBlockUserData.
        self.thisDocument = editor.document()
        
        self._defaultBlockFormat = QTextBlockFormat()
        self._defaultCharFormat = QTextCharFormat()
        self._misspelledColor = Qt.red
        self.style = t2tHighlighterStyle(self.editor, self._defaultCharFormat, style)
        
        self.inDocRules = []

        rules = [
            (r'^\s*[-=_]{20,}\s*$', State.HORIZONTAL_LINE),
            (r'^\s*(\+{1})([^\+].*[^\+])(\+{1})(\[[A-Za-z0-9_-]*\])?\s*$', State.NUMBERED_TITLE_1),
            (r'^\s*(\+{2})([^\+].*[^\+])(\+{2})(\[[A-Za-z0-9_-]*\])?\s*$', State.NUMBERED_TITLE_2),
            (r'^\s*(\+{3})([^\+].*[^\+])(\+{3})(\[[A-Za-z0-9_-]*\])?\s*$', State.NUMBERED_TITLE_3),
            (r'^\s*(\+{4})([^\+].*[^\+])(\+{4})(\[[A-Za-z0-9_-]*\])?\s*$', State.NUMBERED_TITLE_4),
            (r'^\s*(\+{5})([^\+].*[^\+])(\+{5})(\[[A-Za-z0-9_-]*\])?\s*$', State.NUMBERED_TITLE_5),
            (r'^\s*(={1})([^=].*[^=])(={1})(\[[A-Za-z0-9_-]*\])?\s*$', State.TITLE_1),
            (r'^\s*(={2})([^=].*[^=])(={2})(\[[A-Za-z0-9_-]*\])?\s*$', State.TITLE_2),
            (r'^\s*(={3})([^=].*[^=])(={3})(\[[A-Za-z0-9_-]*\])?\s*$', State.TITLE_3),
            (r'^\s*(={4})([^=].*[^=])(={4})(\[[A-Za-z0-9_-]*\])?\s*$', State.TITLE_4),
            (r'^\s*(={5})([^=].*[^=])(={5})(\[[A-Za-z0-9_-]*\])?\s*$', State.TITLE_5),
            (r'^%!.*$', State.SETTINGS_LINE),
            (r'^%[^!]?.*$', State.COMMENT_LINE),
            (r'^\t.+$', State.BLOCKQUOTE_LINE),
            (r'^(```)(.+)$', State.CODE_LINE),
            (r'^(""")(.+)$', State.RAW_LINE),
            (r'^(\'\'\')(.+)$', State.TAGGED_LINE),
            (r'^\s*[-+:] [^ ].*$', State.LIST_BEGINS),
            (r'^\s*[-+:]\s*$', State.LIST_ENDS),
            (r'^ *\|\| .*$', State.TABLE_HEADER),
            (r'^ *\| .*$', State.TABLE_LINE)
        ]

        # Generate rules to identify blocks
        State.Rules = [(QRegExp(pattern), state)
                       for (pattern, state) in rules]
        State.Recursion = 0

    def setDefaultBlockFormat(self, bf):
        self._defaultBlockFormat = bf
        self.rehighlight()
        
    def setDefaultCharFormat(self, cf):
        self._defaultCharFormat = cf
        self.setStyle()
        self.rehighlight()
    
    def setMisspelledColor(self, color):
        self._misspelledColor = color
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """

        # Check if syntax highlighting is enabled
        if self.style is None:
            default = QTextBlockFormat()
            QTextCursor(self.currentBlock()).setBlockFormat(default)
            print("t2tHighlighter.py: is style supposed to be None?")
            return
        
        QTextCursor(self.currentBlock()).setBlockFormat(self._defaultBlockFormat)
        
        block = self.currentBlock()
        oldState = blockUserData.getUserState(block)
        self.identifyBlock(block)
        # formatBlock prevent undo/redo from working
        # TODO: find a todo/undo compatible way of formatting block
        #self.formatBlock(block)

        state = blockUserData.getUserState(block)
        data = blockUserData.getUserData(block)
        inList = self.isList(block)

        op = self.style.format(State.MARKUP)

        #self.setFormat(0, len(text), self.style.format(State.DEFAULT))
        self.setFormat(0, len(text), self._defaultCharFormat)

        # InDocRules: is it a settings which might have a specific rule,
        # a comment which contains color infos, or a include conf?
        # r'^%!p[or][se]t?proc[^\s]*\s*:\s*\'(.*)\'\s*\'.*\''
        rlist = [QRegExp(r'^%!p[or][se]t?proc[^\s]*\s*:\s*((\'[^\']*\'|\"[^\"]*\")\s*(\'[^\']*\'|\"[^\"]*\"))'), # pre/postproc
                 QRegExp(r'^%.*\s\((.*)\)'),                                   # comment
                 QRegExp(r'^%!includeconf:\s*([^\s]*)\s*')]                    # includeconf
        for r in rlist:
            if r.indexIn(text) != -1:
                self.parseInDocRules()

        # Format the whole line:
        for lineState in [
            State.BLOCKQUOTE_LINE,
            State.HORIZONTAL_LINE,
            State.HEADER_LINE,
            ]:
            if not inList and state == lineState:
                self.setFormat(0, len(text), self.style.format(lineState))

        for (lineState, marker) in [
            (State.COMMENT_LINE, "%"),
            (State.CODE_LINE, "```"),
            (State.RAW_LINE, "\"\"\""),
            (State.TAGGED_LINE, "'''"),
            (State.SETTINGS_LINE, "%!")
            ]:
            if state == lineState and \
               not (inList and state == State.SETTINGS_LINE):
                n = 0
                # If it's a comment, we want to highlight all '%'.
                if state == State.COMMENT_LINE:
                    while text[n:n + 1] == "%":
                        n += 1
                    n -= 1

                # Apply Format
                self.setFormat(0, len(marker) + n, op)
                self.setFormat(len(marker) + n,
                               len(text) - len(marker) - n,
                               self.style.format(lineState))

                # If it's a setting, we might do something
                if state == State.SETTINGS_LINE:
                    # Target
                    r = QRegExp(r'^%!([^\s]+)\s*:\s*(\b\w*\b)$')
                    if r.indexIn(text) != -1:
                        setting = r.cap(1)
                        val = r.cap(2)
                        if setting == "target" and \
                           val in self.editor.main.targetsNames:
                            self.editor.fileWidget.preview.setPreferredTarget(val)
                    
                    # Pre/postproc
                    r = QRegExp(r'^%!p[or][se]t?proc[^\s]*\s*:\s*((\'[^\']*\'|\"[^\"]*\")\s*(\'[^\']*\'|\"[^\"]*\"))')
                    if r.indexIn(text) != -1:
                        p = r.pos(1)
                        length = len(r.cap(1))
                        self.setFormat(p, length, self.style.makeFormat(base=self.format(p),
                                                                        fixedPitch=True))

        # Tables
        for lineState in [State.TABLE_LINE, State.TABLE_HEADER]:
            if state == lineState:
                for i in range(len(text)):
                    if text[i] == "|":
                        self.setFormat(i, 1, op)
                    else:
                        self.setFormat(i, 1, self.style.format(lineState))

        # Lists
        #if text == "  p": print(data.isList())
        if data.isList():
            r = QRegExp(r'^\s*[\+\-\:]? ?')
            r.indexIn(text)
            self.setFormat(0, r.matchedLength(), self.style.format(State.LIST_BULLET))
        #if state == State.LIST_BEGINS:
            #r = QRegExp(r'^\s*[+-:] ')
            #r.indexIn(text)
            #self.setFormat(0, r.matchedLength(), self.style.format(State.LIST_BULLET))

        if state == State.LIST_ENDS:
            self.setFormat(0, len(text), self.style.format(State.LIST_BULLET_ENDS))

        # Titles
        if not inList and state in State.TITLES:
            r = [i for (i, s) in State.Rules if s == state][0]
            pos = r.indexIn(text)
            if pos >= 0:
                f = self.style.format(state)
                # Uncomment for markup to be same size as title
                #op = self.formats(preset="markup",
                                  #base=self.formats(preset=state))
                self.setFormat(r.pos(2), len(r.cap(2)), f)
                self.setFormat(r.pos(1), len(r.cap(1)), op)
                self.setFormat(r.pos(3), len(r.cap(3)), op)

        # Areas: comment, code, raw tagged
        for (begins, middle, ends) in [
            (State.COMMENT_AREA_BEGINS, State.COMMENT_AREA, State.COMMENT_AREA_ENDS),
            (State.CODE_AREA_BEGINS, State.CODE_AREA, State.CODE_AREA_ENDS),
            (State.RAW_AREA_BEGINS, State.RAW_AREA, State.RAW_AREA_ENDS),
            (State.TAGGED_AREA_BEGINS, State.TAGGED_AREA, State.TAGGED_AREA_ENDS),
            ]:

            if state == middle:
                self.setFormat(0, len(text), self.style.format(middle))
            elif state in [begins, ends]:
                self.setFormat(0, len(text), op)

        # Inline formatting
        if state not in [
            #State.COMMENT_AREA,
            #State.COMMENT_LINE,
            State.RAW_AREA,
            State.RAW_LINE,
            State.CODE_AREA,
            State.CODE_LINE,
            State.TAGGED_AREA,
            State.TAGGED_LINE,
            State.SETTINGS_LINE,
            State.HORIZONTAL_LINE,
            ] and state not in State.TITLES:
            formatArray = textToFormatArray(text)

            # InDocRules
            for (r, c) in self.inDocRules:
                i = re.finditer(r.decode('utf8'), text, re.UNICODE)
                for m in i:
                    f = self.format(m.start())
                    l = m.end() - m.start()
                    if "," in c:
                        c1, c2 = c.split(",")
                        self.setFormat(m.start(), l,
                                   self.style.makeFormat(color=c1, bgcolor=c2, base=f))
                    else:
                        self.setFormat(m.start(), l,
                                   self.style.makeFormat(color=c, base=f))

            # Links 
            if state not in [State.COMMENT_LINE, State.COMMENT_AREA]:
                r = QRegExp(r'\[(\[[^\]]*\])?[^\]]*\s*([^\s]+)\]')
                r.setMinimal(False)
                pos = r.indexIn(text)
                links = []
                while pos >= 0:
                    #TODO: The text should not be formatted if [**not bold**]
                    #if max([k[pos] for k in formatArray]) == 0 or 1 == 1:
                    self.setFormat(pos, 1,
                                   self.style.format(State.MARKUP))
                    self.setFormat(pos + 1, len(r.cap(0)) - 1,
                                   self.style.format(State.LINKS))
                    self.setFormat(pos + len(r.cap(0)) - 1, 1,
                                   self.style.format(State.MARKUP))
                    if r.pos(2) > 0:
                        _f = QTextCharFormat(self.style.format(State.LINKS))
                        _f.setForeground(QBrush(_f.foreground()
                                                      .color().lighter()))
                        _f.setFontUnderline(True)
                        self.setFormat(r.pos(2), len(r.cap(2)), _f)
                        
                    links.append([pos, len(r.cap(0))]) # To remember for the next highlighter (single links)
                    pos = r.indexIn(text, pos + 1)
                    
                # Links like www.theologeek.ch, http://www.fsf.org, ...
                # FIXME: - "http://adresse et http://adresse" is detected also as italic
                #        - some error, like "http://adress.htm." also color the final "."
                #        - also: adresse@email.com, ftp://, www2, www3, etc.
                #        - But for now, does the job
                r = QRegExp(r'http://[^\s]*|www\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+[^\s]*')
                #r.setMinimal(True)
                pos = r.indexIn(text)
                while pos >= 0:
                    for k in links:
                        #print pos, k[0], k[1]
                        if pos > k[0] and pos < k[0] + k[1]:  # already highlighted
                            break
                    else:
                        self.setFormat(pos, len(r.cap(0)), self.style.format(State.LINKS))
                    
                    pos = r.indexIn(text, pos + 1)

            # Bold, Italic, Underline, Code, Tagged, Strikeout
            for i in range(len(text)):
                f = self.format(i)
                beautifiers = [k[i] for k in formatArray]
                self.setFormat(i, 1, self.style.beautifyFormat(f, beautifiers))

            # Macro words
            for r in [r'(%%)\b\w+\b', r'(%%)\b\w+\b\(.+\)']:
                r = QRegExp(r)
                r.setMinimal(True)
                pos = r.indexIn(text)
                while pos >= 0:
                    if max([k[pos] for k in formatArray]) == 0:
                        self.setFormat(pos, len(r.cap(0)),
                                       self.style.format(State.MACRO))
                    pos = r.indexIn(text, pos + 1)
        
        # Highlighted word (for search)
        if self.editor.highlightWord:
            if self.editor.highligtCS and self.editor.highlightWord in text or \
               not self.editor.highlightCs and self.editor.highlightWord.lower() in text.lower():
                #if self.editor.highlightCS:
                    #s = self.editor.highlightWord
                #else:
                    #s = self.editor.highlightWord.toLower()
                #print(s)
                p = text.indexOf(self.editor.highlightWord, cs=self.editor.highlightCS)
                while p >= 0:
                    self.setFormat(p, len(self.editor.highlightWord),
                                   self.style.makeFormat(preset="higlighted", base=self.format(p)))
                    p = text.indexOf(self.editor.highlightWord, p + 1, cs=self.editor.highlightCS)
            
            
        ### Highlight Selection
        ### TODO: way to slow, find another way.
        ##sel = self.editor.textCursor().selectedText()
        ##if len(sel) > 5: self.keywordRules.append((QRegExp(sel), "selected"))

        ## Do keyword formatting
        #for expression, style in self.keywordRules:
            #expression.setMinimal( True )
            #index = expression.indexIn(text, 0)

            ## There might be more than one on the same line
            #while index >= 0:
                #length = expression.cap(0).length()
                #f = self.formats(preset=style, base=self.formats(index))
                #self.setFormat(index, length, f)
                #index = expression.indexIn(text, index + length)
        
        # Spell checking
        # Based on http://john.nachtimwald.com/2009/08/22/qplaintextedit-with-in-line-spell-check/
        WORDS = '(?iu)[\w\']+'
        if state not in [State.SETTINGS_LINE]:
            if self.editor.spellcheck:
                for word_object in re.finditer(WORDS, text):
                    if self.editor._dict and not self.editor._dict.check(word_object.group()):
                        format = self.format(word_object.start())
                        format.setUnderlineColor(self._misspelledColor)
                        format.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                        self.setFormat(word_object.start(),
                            word_object.end() - word_object.start(), format)

    def identifyBlock(self, block):
        """Identifies what block type it is, and set userState and userData
        accordingly."""

        text = block.text()
        data = blockUserData.getUserData(block)

        # Header Lines
        # No header line here
        #if block.blockNumber() == 0:
            #block.setUserState(State.HEADER_LINE)
            #return
        #elif block.blockNumber() in [1, 2] and \
             #self.document().findBlockByNumber(0).text():
            #block.setUserState(State.HEADER_LINE)
            #return

        state = 0
        inList = False
        blankLinesBefore = 0

        #if text.contains(QRegExp(r'^\s*[-+:] [^ ].*[^-+]{1}\s*$')):
        if QRegExp(r'^\s*[-+:] [^ ].*[^-+]{1}\s*$').indexIn(text) != -1:    
            state = State.LIST_BEGINS

        # List stuff
        if self.isList(block.previous()) or state == State.LIST_BEGINS:
            inList = True

            # listLevel and leadingSpaces
            #FIXME: not behaving exactly correctly...
            lastData = blockUserData.getUserData(block.previous())
            if state == State.LIST_BEGINS:
                leadingSpaces = QRegExp(r'[-+:]').indexIn(text, 0)
                data.setLeadingSpaces(leadingSpaces)
                
                data.setListSymbol(text[leadingSpaces])
                if self.isList(block.previous()):
                    # The last block was also a list.
                    # We need to check if this is the same level, or a sublist
                    if leadingSpaces > lastData.leadingSpaces():
                        # This is a sublevel list
                        data.setListLevel(lastData.listLevel() + 1)
                    else:
                        # This is same level
                        data.setListLevel(lastData.listLevel())
                else:
                    data.setListLevel(1)
            else:
                data.setListLevel(lastData.listLevel())
                data.setLeadingSpaces(lastData.leadingSpaces())
                data.setListSymbol(lastData.listSymbol())

            # Blank lines before (two = end of list)
            blankLinesBefore = self.getBlankLines(block.previous())
            if not QRegExp(r'^\s*$').indexIn(block.previous().text()) != -1 and \
               not blockUserData.getUserState(block.previous()) in [State.COMMENT_LINE,
                   State.COMMENT_AREA, State.COMMENT_AREA_BEGINS,
                   State.COMMENT_AREA_ENDS]:
                blankLinesBefore = 0
            elif not blockUserData.getUserState(block.previous()) in \
                 [State.COMMENT_LINE, State.COMMENT_AREA,
                  State.COMMENT_AREA_BEGINS, State.COMMENT_AREA_ENDS]:
                blankLinesBefore += 1
            if blankLinesBefore == 2:
                # End of list.
                blankLinesBefore = 0
                inList = False
            if inList and QRegExp(r'^\s*$').indexIn(text) != -1:
                state = State.LIST_EMPTY

        # Areas
        for (begins, middle, ends, marker) in [
            (State.COMMENT_AREA_BEGINS, State.COMMENT_AREA, State.COMMENT_AREA_ENDS, "^%%%\s*$"),
            (State.CODE_AREA_BEGINS, State.CODE_AREA, State.CODE_AREA_ENDS, "^```\s*$"),
            (State.RAW_AREA_BEGINS, State.RAW_AREA, State.RAW_AREA_ENDS, "^\"\"\"\s*$"),
            (State.TAGGED_AREA_BEGINS, State.TAGGED_AREA, State.TAGGED_AREA_ENDS, '^\'\'\'\s*$'),
            ]:

            if QRegExp(marker).indexIn(text) != -1:
                if blockUserData.getUserState(block.previous()) in [begins, middle]:
                    state = ends
                    break
                else:
                    state = begins
                    break
            if blockUserData.getUserState(block.previous()) in [middle, begins]:
                state = middle
                break

        # Patterns (for lines)
        if not state:
            for (pattern, lineState) in State.Rules:
                pos = pattern.indexIn(text)
                if pos >= 0:
                    state = lineState
                    break

        if state in [State.BLOCKQUOTE_LINE, State.LIST_ENDS]:
            #FIXME: doesn't work exactly. Closes only the current level, not
            #FIXME: the whole list.
            inList = False

        if inList and not state == State.LIST_BEGINS:
            state += 100
            if blankLinesBefore:
                state += 100

        block.setUserState(state)
        block.setUserData(data)

    def formatBlock(self, block):
        """
        Formats the block according to its state.
        """
        #TODO: Use QTextDocument format presets, and QTextBlock's
        #TODO: blockFormatIndex. And move that in t2tHighlighterStyle.
        state = block.userState()
        blockFormat = QTextBlockFormat()

        if state in [State.BLOCKQUOTE_LINE,
                     State.HEADER_LINE] + State.LIST:
            blockFormat = self.style.formatBlock(block, state)

        QTextCursor(block).setBlockFormat(blockFormat)

    def getBlankLines(self, block):
        "Returns if there is a blank line before in the list."
        state = block.userState()
        if state >= 200:
            return 1
        else:
            return 0

    def isList(self, block):
        "Returns TRUE if the block is in a list."
        if block.userState() == State.LIST_BEGINS or\
           block.userState() >= 100:
            return True

    def setStyle(self, style="Default"):
        if style in t2tHighlighterStyle.validStyles:
            self.style = t2tHighlighterStyle(self.editor, self._defaultCharFormat, style)
        else:
            self.style = None
        self.rehighlight()

    def setFontPointSize(self, size):
        self.defaultFontPointSize = size
        self.style = t2tHighlighterStyle(self.editor, self.style.name)
        self.rehighlight()

    def parseInDocRules(self):
        oldRules = self.inDocRules
        self.inDocRules = []

        t = self.thisDocument.toPlainText()
        
        # Get all conf files
        confs = []
        lines = t.split("\n")
        for l in lines:
            r = QRegExp(r'^%!includeconf:\s*([^\s]*)\s*')
            if r.indexIn(l) != -1:
                confs.append(r.cap(1))
        
        # Try to load conf files
        for c in confs:
            try:
                import codecs
                f = self.editor.fileWidget.file
                d = QDir.cleanPath(QFileInfo(f).absoluteDir().absolutePath()+"/"+c)
                file = codecs.open(d, 'r', "utf-8")
            except:
                print(("Error: cannot open {}.".format(c)))
                continue 
            # We add the content to the current lines of the current document
            lines += file.readlines() #lines.extend(file.readlines())
            
        #b = self.thisDocument.firstBlock()
        lastColor = ""
        
        #while b.isValid():
        for l in lines:
            text = l #b.text()
            r = QRegExp(r'^%!p[or][se]t?proc[^\s]*\s*:\s*(\'[^\']*\'|\"[^\"]*\")\s*(\'[^\']*\'|\"[^\"]*\")')
            if r.indexIn(text) != -1:
                rule = r.cap(1)[1:-1]
                # Check if there was a color-comment above that post/preproc bloc
                if lastColor:
                    self.inDocRules.append((str(rule), lastColor))
                # Check if previous block is a comment like it should
                else:
                    previousText = lines[lines.indexOf(l)-1] #b.previous().text()
                    r = QRegExp(r'^%.*\s\((.*)\)')
                    if r.indexIn(previousText) != -1:
                        lastColor = r.cap(1)
                        self.inDocRules.append((str(rule), lastColor))
            else:
                lastColor = ""
            #b = b.next()

        if oldRules != self.inDocRules:
            #Rules have changed, we need to rehighlight
            #print("Rules have changed.", len(self.inDocRules))
            #self.rehighlight()  # Doesn't work (seg fault), why?
            pass
            #b = self.thisDocument.firstBlock()
            #while b.isValid():
                #for (r, c) in self.inDocRules:
                    #r = QRegExp(r)
                    #pos = r.indexIn(b.text())
                    #if pos >= 0:
                        #print("rehighlighting:", b.text())
                        #self.rehighlightBlock(b)
                        #break
                #b = b.next()
