from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QTextEdit

MODE_NORMAL = '-- NORMAL --'
MODE_INSERT = '-- INSERT --'


def _char_class(ch, big):
    if ch.isspace():
        return 0
    if big:
        return 1
    if ch.isalnum() or ch == '_':
        return 1
    return 2


def _motion_w(text, position, big, count):
    n = len(text)
    for _ in range(count):
        if position >= n:
            break
        cls = _char_class(text[position], big)
        if cls == 0:
            while position < n and _char_class(text[position], big) == 0:
                position += 1
        else:
            while position < n and _char_class(text[position], big) == cls:
                position += 1
            while position < n and _char_class(text[position], big) == 0:
                position += 1
    return position


def _motion_b(text, position, big, count):
    for _ in range(count):
        if position <= 0:
            break
        position -= 1
        while position > 0 and _char_class(text[position], big) == 0:
            position -= 1
        cls = _char_class(text[position], big)
        if cls != 0:
            while position > 0 and _char_class(text[position - 1], big) == cls:
                position -= 1
    return position


def _motion_e(text, position, big, count):
    n = len(text)
    for _ in range(count):
        if position >= n - 1:
            break
        position += 1
        while position < n and _char_class(text[position], big) == 0:
            position += 1
        if position >= n:
            position = max(n - 1, 0)
            break
        cls = _char_class(text[position], big)
        while position + 1 < n and _char_class(text[position + 1], big) == cls and cls != 0:
            position += 1
    return position


class VimMode(QObject):
    modeChanged = pyqtSignal(str)

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.mode = MODE_NORMAL
        self.count = ''
        self.operator_count = 0
        self.pending_operator = None
        self.pending_motion = None
        self.register = ''
        self.register_linewise = False
        self.last_find = None
        self._orig_cursor_width = editor.cursorWidth()
        editor.cursorPositionChanged.connect(self._onCursorPositionChanged)
        self.refreshBlockCursor()

    # -- public API --

    def handleKey(self, event):
        if self.mode == MODE_INSERT:
            if event.key() == Qt.Key_Escape or (
                    event.key() == Qt.Key_BracketLeft and event.modifiers() & Qt.ControlModifier):
                self._enterNormal()
                return True
            return False
        return self._handleNormalKey(event)

    def reset(self):
        self._cancelPending()
        self.mode = MODE_NORMAL
        self.modeChanged.emit(self.mode)
        self.refreshBlockCursor()

    def refreshIndicator(self):
        self.modeChanged.emit(self.mode)

    # -- mode transitions --

    def _enterNormal(self):
        cursor = self.editor.textCursor()
        if cursor.positionInBlock() > 0:
            cursor.movePosition(QTextCursor.Left)
            self.editor.setTextCursor(cursor)
        self._cancelPending()
        self.mode = MODE_NORMAL
        self.modeChanged.emit(self.mode)
        self.refreshBlockCursor()

    def _enterInsert(self):
        self._cancelPending()
        self.mode = MODE_INSERT
        self.modeChanged.emit(self.mode)
        self.refreshBlockCursor()

    def _cancelPending(self):
        self.count = ''
        self.operator_count = 0
        self.pending_operator = None
        self.pending_motion = None

    def _takeCount(self):
        c = int(self.count) if self.count else 1
        self.count = ''
        return c

    # -- helpers --

    def _text(self):
        return self.editor.toPlainText()

    def _document(self):
        return self.editor.document()

    def _firstNonBlank(self, block):
        t = block.text()
        return block.position() + len(t) - len(t.lstrip())

    def _lastLineBlock(self):
        b = self._document().lastBlock()
        if b.position() == len(self._text()) and b.previous().isValid():
            b = b.previous()
        return b

    def _setCursorPos(self, pos, fnb=False):
        pos = max(0, min(pos, self._document().characterCount() - 1))
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        if fnb:
            block = cursor.block()
            t = block.text()
            cursor.setPosition(block.position() + len(t) - len(t.lstrip()))
        self.editor.setTextCursor(cursor)

    def _onCursorPositionChanged(self):
        if self.mode == MODE_NORMAL:
            self.refreshBlockCursor()

    def refreshBlockCursor(self):
        if self.mode != MODE_NORMAL:
            self.editor.setExtraSelections([])
            self.editor.setCursorWidth(self._orig_cursor_width)
            return
        cursor = self.editor.textCursor()
        block = cursor.block()
        if cursor.positionInBlock() < block.length() - 1:
            selection = QTextEdit.ExtraSelection()
            c = QTextCursor(self.editor.document())
            c.setPosition(cursor.position())
            c.setPosition(cursor.position() + 1, QTextCursor.KeepAnchor)
            selection.cursor = c
            fmt = QTextCharFormat()
            fmt.setBackground(self.editor.palette().highlight())
            fmt.setForeground(self.editor.palette().highlightedText())
            selection.format = fmt
            self.editor.setExtraSelections([selection])
            self.editor.setCursorWidth(0)
        else:
            self.editor.setExtraSelections([])
            self.editor.setCursorWidth(
                self.editor.fontMetrics().horizontalAdvance(" "))

    # -- normal-mode dispatch --

    def _handleNormalKey(self, event):
        k = event.key()
        text = event.text()
        mods = event.modifiers()

        if k == Qt.Key_Escape or (k == Qt.Key_BracketLeft and mods & Qt.ControlModifier):
            self._cancelPending()
            return True

        if self.pending_motion is not None:
            if self.pending_motion == 'g':
                self.pending_motion = None
                if text == 'g':
                    self._executeG(gg=True)
                else:
                    self._cancelPending()
            else:
                self._executeFind(text)
            return True

        if self.pending_operator == 'g' and text and text.isprintable() and not text.isspace():
            if text == 'g':
                self._executeG(gg=True)
            else:
                self._cancelPending()
            return True

        if self.pending_operator == 'r' and text and len(text) == 1 and text.isprintable():
            self._executeReplace(text)
            return True

        if mods & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            if (mods & Qt.ControlModifier) and not (mods & Qt.ShiftModifier) and k == Qt.Key_R:
                self._cancelPending()
                self.editor.redo()
                return True
            if (mods & Qt.ControlModifier) and k == Qt.Key_V:
                return True
            return False

        if text and len(text) == 1 and text.isprintable() and not text.isspace():
            if text.isdigit() and not (text == '0' and self.count == ''):
                self.count += text
                return True
            if self.pending_operator is not None:
                self._handleOperatorKey(text)
                return True
            if text in 'dcy':
                self.pending_operator = text
                self.operator_count = int(self.count) if self.count else 0
                self.count = ''
                return True
            self._handleCommandKey(text)
            return True

        return self._handleSpecialKey(event)

    def _handleCommandKey(self, ch):
        if ch == 'i':
            self.count = ''
            self._enterInsert()
        elif ch in 'hljk':
            self._executeMove(ch)
        elif ch in '0^$':
            self._executeLineMotion(ch)
        elif ch == 'g':
            self.pending_operator = 'g'
            self.operator_count = int(self.count) if self.count else 0
            self.count = ''
        elif ch == 'G':
            self._executeG()
        elif ch == 'x':
            self._executeDeleteChars()
        elif ch == 'r':
            self.pending_operator = 'r'
            self.operator_count = int(self.count) if self.count else 0
            self.count = ''
        elif ch in 'aAIoO':
            self._executeInsertGesture(ch)
        elif ch == 'J':
            self._executeJoin()
        elif ch == 'u':
            self._takeCount()
            self._cancelPending()
            self.editor.undo()
        elif ch == 'D':
            cursor = self.editor.textCursor()
            self._takeCount()
            self._operateRange('d', cursor.position(),
                               cursor.block().position() + max(cursor.block().length() - 1, 0))
        elif ch == 'C':
            cursor = self.editor.textCursor()
            self._takeCount()
            self._operateRange('c', cursor.position(),
                               cursor.block().position() + max(cursor.block().length() - 1, 0))
        elif ch == 'p':
            self._executePaste(True, self._takeCount())
        elif ch == 'P':
            self._executePaste(False, self._takeCount())
        elif ch in 'wWbBeE':
            self._executeWordMotion(ch)
        elif ch in 'ftFT':
            self.pending_motion = ch
        elif ch in ';,':
            if self.last_find is not None:
                cmd, fch = self.last_find
                if ch == ',':
                    cmd = {'f': 'F', 'F': 'f', 't': 'T', 'T': 't'}[cmd]
                for _ in range(int(self.count) if self.count else 1):
                    if not self._find_char(cmd, fch, store=False):
                        break
                self.count = ''

    # -- motions --

    def _executeMove(self, ch):
        count = self._takeCount()
        cursor = self.editor.textCursor()
        block = cursor.block()
        position = cursor.position()
        if ch == 'h':
            self._setCursorPos(max(block.position(), position - count))
        elif ch == 'l':
            self._setCursorPos(min(block.position() + max(block.length() - 2, 0), position + count))
        else:
            self._executeVerticalMove(ch == 'j', count)

    def _executeVerticalMove(self, down, count):
        cursor = self.editor.textCursor()
        block = cursor.block()
        col = cursor.positionInBlock()
        for _ in range(count):
            nxt = block.next() if down else block.previous()
            if not nxt.isValid() or nxt.position() >= len(self._text()):
                break
            block = nxt
        col = min(col, max(block.length() - 2, 0))
        self._setCursorPos(block.position() + col)

    def _executeLineMotion(self, ch):
        count = self._takeCount()
        block = self.editor.textCursor().block()
        if ch == '0':
            self._setCursorPos(block.position())
            return
        if ch == '^':
            self._setCursorPos(self._firstNonBlank(block))
            return
        target = block.position() + max(block.length() - 2, 0)
        for _ in range(count - 1):
            nxt = block.next()
            if not nxt.isValid() or nxt.position() >= len(self._text()):
                break
            block = nxt
            target = block.position() + max(block.length() - 2, 0)
        self._setCursorPos(target)

    def _executeG(self, gg=False):
        op = self.pending_operator if self.pending_operator in ('d', 'c', 'y') else None
        count = int(self.count) if self.count else 0
        op_count = self.operator_count
        cursor_block = self.editor.textCursor().block()
        self._cancelPending()
        if op is not None:
            if count or op_count:
                n = (op_count or 1) * (count or 1)
                target = self._document().findBlockByNumber(n - 1)
                if not target.isValid():
                    target = self._lastLineBlock()
            else:
                target = self._document().firstBlock() if gg else self._lastLineBlock()
            first, last = (cursor_block, target) if cursor_block.position() <= target.position() else (target, cursor_block)
            self._applyLinewiseRange(op, first, last)
            return
        if count:
            block = self._document().findBlockByNumber(count - 1)
            if not block.isValid():
                block = self._lastLineBlock()
        else:
            block = self._document().firstBlock() if gg else self._lastLineBlock()
        self._setCursorPos(block.position(), fnb=True)

    # -- special keys --

    def _handleSpecialKey(self, event):
        k = event.key()
        if k in (Qt.Key_Return, Qt.Key_Enter):
            self._takeCount()
            nxt = self.editor.textCursor().block().next()
            if nxt.isValid() and nxt.position() < len(self._text()):
                self._setCursorPos(nxt.position(), fnb=True)
            return True
        if k == Qt.Key_Backspace:
            count = self._takeCount()
            cursor = self.editor.textCursor()
            self._setCursorPos(max(cursor.block().position(), cursor.position() - count))
            return True
        if k == Qt.Key_Space:
            count = self._takeCount()
            cursor = self.editor.textCursor()
            end = cursor.block().position() + max(cursor.block().length() - 2, 0)
            self._setCursorPos(min(end, cursor.position() + count))
            return True
        if k == Qt.Key_Delete:
            self._executeDeleteChars()
            return True
        if k == Qt.Key_Tab:
            self._takeCount()
            return True
        return False

    def _executeWordMotion(self, ch):
        count = self._takeCount()
        self._cancelPending()
        big = ch.isupper()
        text = self._text()
        position = self.editor.textCursor().position()
        if ch in 'wW':
            position = _motion_w(text, position, big, count)
        elif ch in 'bB':
            position = _motion_b(text, position, big, count)
        else:
            position = _motion_e(text, position, big, count)
        self._setCursorPos(position)

    def _executeFind(self, ch):
        cmd = self.pending_motion
        self.pending_motion = None
        if not ch or not ch.isprintable():
            self._cancelPending()
            return
        op = self.pending_operator if self.pending_operator in ('d', 'c', 'y') else None
        if op is not None:
            text = self._text()
            position = self.editor.textCursor().position()
            if cmd in 'ft':
                idx = text.find(ch, position + 1)
            else:
                idx = text.rfind(ch, 0, position)
            if idx < 0:
                self._cancelPending()
                return
            if cmd == 'f':
                start, end = position, idx + 1
            elif cmd == 't':
                start, end = position, idx
            elif cmd == 'F':
                start, end = idx, position + 1
            else:
                start, end = idx + 1, position
            self._cancelPending()
            if start != end:
                self._operateRange(op, start, end)
            return
        for _ in range(int(self.count) if self.count else 1):
            if not self._find_char(cmd, ch):
                break
        self.count = ''

    def _find_char(self, cmd, ch, store=True):
        text = self._text()
        position = self.editor.textCursor().position()
        if cmd in 'ft':
            idx = text.find(ch, position + 1)
        else:
            idx = text.rfind(ch, 0, position)
        if idx < 0:
            return False
        if store:
            self.last_find = (cmd, ch)
        if cmd == 'f':
            self._setCursorPos(idx)
        elif cmd == 't':
            self._setCursorPos(idx - 1)
        elif cmd == 'F':
            self._setCursorPos(idx)
        else:
            self._setCursorPos(idx + 1)
        return True

    def _executeReplace(self, ch):
        count = self.operator_count if self.operator_count else 1
        self._cancelPending()
        cursor = self.editor.textCursor()
        block = cursor.block()
        position = cursor.position()
        line_end = block.position() + block.length() - 1
        end = min(position + count, line_end, len(self._text()))
        if end <= position:
            return
        edit_cursor = QTextCursor(self._document())
        edit_cursor.setPosition(position)
        edit_cursor.setPosition(end, QTextCursor.KeepAnchor)
        edit_cursor.beginEditBlock()
        edit_cursor.insertText(ch * (end - position))
        edit_cursor.endEditBlock()
        self._setCursorPos(position)

    def _executeDeleteChars(self):
        count = self._takeCount()
        text = self._text()
        position = self.editor.textCursor().position()
        end = position
        while end < len(text) and end - position < count and text[end] != '\n':
            end += 1
        if end == position:
            return
        self.register = text[position:end]
        self.register_linewise = False
        edit_cursor = QTextCursor(self._document())
        edit_cursor.setPosition(position)
        edit_cursor.setPosition(end, QTextCursor.KeepAnchor)
        edit_cursor.beginEditBlock()
        edit_cursor.removeSelectedText()
        edit_cursor.endEditBlock()
        self._setCursorPos(position)

    def _executeJoin(self):
        count = int(self.count) if self.count else 1
        self.count = ''
        edit_cursor = QTextCursor(self._document())
        edit_cursor.beginEditBlock()
        for _ in range(count):
            cursor = self.editor.textCursor()
            block = cursor.block()
            nxt = block.next()
            text = self._text()
            if not nxt.isValid() or nxt.position() >= len(text):
                break
            eob = block.position() + block.length() - 1
            text_next = nxt.text()
            if text_next.strip() == '':
                end = nxt.position()
                replacement = ''
            else:
                end = nxt.position() + len(text_next) - len(text_next.lstrip())
                replacement = ' '
            edit_cursor.setPosition(eob)
            edit_cursor.setPosition(end, QTextCursor.KeepAnchor)
            edit_cursor.insertText(replacement)
            self._setCursorPos(eob)
        edit_cursor.endEditBlock()

    def _executeInsertGesture(self, ch):
        cursor = self.editor.textCursor()
        block = cursor.block()
        position = cursor.position()
        eob = block.position() + block.length() - 1
        text = self._text()
        if ch == 'a':
            position = position + 1 if position < len(text) else position
        elif ch == 'I':
            position = self._firstNonBlank(block)
        elif ch == 'A':
            position = eob
        elif ch == 'o':
            edit_cursor = QTextCursor(self._document())
            edit_cursor.setPosition(eob)
            edit_cursor.beginEditBlock()
            edit_cursor.insertText('\n')
            edit_cursor.endEditBlock()
            position = eob + 1
        else:  # 'O'
            edit_cursor = QTextCursor(self._document())
            edit_cursor.setPosition(block.position())
            edit_cursor.beginEditBlock()
            edit_cursor.insertText('\n')
            edit_cursor.endEditBlock()
            position = block.position()
        self._setCursorPos(position)
        self._enterInsert()

    # -- operators --

    def _handleOperatorKey(self, ch):
        op = self.pending_operator
        cursor = self.editor.textCursor()
        block = cursor.block()
        position = cursor.position()
        text = self._text()

        if ch == op:
            count = (self.operator_count or 1) * self._takeCount()
            self._cancelPending()
            self._applyLinewiseRange(op, block, self._blockBelow(block, count - 1))
            return
        if ch == 'G':
            self._executeG()
            return
        if ch == 'g':
            self.pending_motion = 'g'
            return
        if ch in 'ftFT':
            self.pending_motion = ch
            return

        count = (self.operator_count or 1) * self._takeCount()
        if ch in 'jk':
            if ch == 'j':
                first, last = block, self._blockBelow(block, count)
            else:
                first, last = self._blockAbove(block, count), block
            self._cancelPending()
            self._applyLinewiseRange(op, first, last)
            return

        if op == 'c' and ch in 'wW':
            ch = 'e' if ch == 'w' else 'E'
        big = ch.isupper()
        if ch in 'wW':
            target = _motion_w(text, position, big, count)
        elif ch in 'bB':
            target = _motion_b(text, position, big, count)
        elif ch in 'eE':
            target = _motion_e(text, position, big, count)
        elif ch == 'h':
            target = max(block.position(), position - count)
        elif ch == 'l':
            target = min(block.position() + max(block.length() - 2, 0), position + count)
        elif ch == '0':
            target = block.position()
        elif ch == '^':
            target = self._firstNonBlank(block)
        elif ch == '$':
            target = block.position() + max(block.length() - 1, 0)
        else:
            self._cancelPending()
            return

        start = min(position, target)
        end = max(position, target)
        if ch in 'eE':
            end += 1
        self._cancelPending()
        if start >= end and op in ('d', 'c'):
            return
        self._operateRange(op, start, end)

    def _operateRange(self, op, start, end):
        n = self._document().characterCount() - 1
        start = max(0, min(start, n))
        end = max(0, min(end, n))
        self.register = self._text()[start:end]
        self.register_linewise = False
        if op == 'y':
            self._setCursorPos(start)
            return
        if start == end:
            if op == 'c':
                self._enterInsert()
            return
        edit_cursor = QTextCursor(self._document())
        edit_cursor.setPosition(start)
        edit_cursor.setPosition(end, QTextCursor.KeepAnchor)
        edit_cursor.beginEditBlock()
        edit_cursor.removeSelectedText()
        edit_cursor.endEditBlock()
        self._setCursorPos(start)
        if op == 'c':
            self._enterInsert()

    def _applyLinewiseRange(self, op, first, last):
        n = self._document().characterCount() - 1
        start = first.position()
        end = min(last.position() + last.length(), n)
        self.register = self._text()[start:end]
        self.register_linewise = True
        if op == 'y':
            self._setCursorPos(start, fnb=True)
            return
        edit_cursor = QTextCursor(self._document())
        edit_cursor.setPosition(start)
        if op == 'c' and last.next().isValid() and last.next().position() < n:
            edit_cursor.setPosition(end - 1, QTextCursor.KeepAnchor)
        else:
            edit_cursor.setPosition(end, QTextCursor.KeepAnchor)
        edit_cursor.beginEditBlock()
        edit_cursor.removeSelectedText()
        edit_cursor.endEditBlock()
        self._setCursorPos(start, fnb=True)
        if op == 'c':
            self._enterInsert()

    def _blockBelow(self, block, count):
        text = self._text()
        for _ in range(count):
            nxt = block.next()
            if not nxt.isValid() or nxt.position() >= len(text):
                return block
            block = nxt
        return block

    def _blockAbove(self, block, count):
        for _ in range(count):
            nxt = block.previous()
            if not nxt.isValid():
                return block
            block = nxt
        return block

    def _executePaste(self, below, count):
        if not self.register:
            return
        if self.register_linewise:
            reg = self.register.rstrip('\n')
            block = self.editor.textCursor().block()
            edit_cursor = QTextCursor(self._document())
            if below:
                at = block.position() + block.length() - 1
                edit_cursor.setPosition(at)
                edit_cursor.beginEditBlock()
                for _ in range(count):
                    edit_cursor.insertText('\n' + reg)
                edit_cursor.endEditBlock()
                self._setCursorPos(at + 1, fnb=True)
            else:
                at = block.position()
                edit_cursor.setPosition(at)
                edit_cursor.beginEditBlock()
                for _ in range(count):
                    edit_cursor.insertText(reg + '\n')
                edit_cursor.endEditBlock()
                self._setCursorPos(at, fnb=True)
            return
        text = self._text()
        position = self.editor.textCursor().position()
        if below:
            at = position + 1 if position < len(text) and text[position] != '\n' else position
        else:
            at = position
        edit_cursor = QTextCursor(self._document())
        edit_cursor.setPosition(at)
        edit_cursor.beginEditBlock()
        edit_cursor.insertText(self.register * count)
        edit_cursor.endEditBlock()
        self._setCursorPos(at + len(self.register) * count - 1)
