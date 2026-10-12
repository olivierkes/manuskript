from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor

MODE_NORMAL = '-- NORMAL --'
MODE_INSERT = '-- INSERT --'


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

    def _enterInsert(self):
        self._cancelPending()
        self.mode = MODE_INSERT
        self.modeChanged.emit(self.mode)

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

    # -- normal-mode dispatch --

    def _handleNormalKey(self, event):
        k = event.key()
        text = event.text()
        mods = event.modifiers()

        if k == Qt.Key_Escape or (k == Qt.Key_BracketLeft and mods & Qt.ControlModifier):
            self._cancelPending()
            return True

        if self.pending_operator == 'g' and text and text.isprintable() and not text.isspace():
            if text == 'g':
                self._executeG(gg=True)
            else:
                self._cancelPending()
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
        count = int(self.count) if self.count else 0
        self._cancelPending()
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
            self._takeCount()
            return True
        if k == Qt.Key_Tab:
            self._takeCount()
            return True
        return False

    # -- operators (filled in Task 4) --

    def _handleOperatorKey(self, text):
        self._cancelPending()
