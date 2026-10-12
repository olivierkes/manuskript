from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent

from manuskript.ui.views.vimMode import MODE_INSERT, MODE_NORMAL


SPECIAL_KEYS = {
    ' ': (Qt.Key_Space, ' '),
    '\b': (Qt.Key_Backspace, ''),
    '\t': (Qt.Key_Tab, '\t'),
    '$': (Qt.Key_Dollar, '$'),
    '^': (Qt.Key_AsciiCircum, '^'),
    ';': (Qt.Key_Semicolon, ';'),
    ',': (Qt.Key_Comma, ','),
}


def send_key(editor, key, text='', mods=Qt.NoModifier):
    editor.keyPressEvent(QKeyEvent(QEvent.KeyPress, key, mods, text))


def send(editor, keys):
    for ch in keys:
        if ch == '\n':
            send_key(editor, Qt.Key_Return, '\r')
        elif ch in SPECIAL_KEYS:
            key, text = SPECIAL_KEYS[ch]
            send_key(editor, key, text)
        elif ch.isalpha():
            if ch.isupper():
                send_key(editor, getattr(Qt, 'Key_' + ch), ch, Qt.ShiftModifier)
            else:
                send_key(editor, getattr(Qt, 'Key_' + ch.upper()), ch)
        elif ch.isdigit():
            send_key(editor, getattr(Qt, 'Key_' + ch), ch)
        else:
            raise ValueError('unmapped key: %r' % ch)


def esc(editor):
    send_key(editor, Qt.Key_Escape)


def load(editor, text, position=0):
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.setPosition(position)
    editor.setTextCursor(cursor)


def pos(editor):
    return editor.textCursor().position()


def test_starts_in_normal_mode(editor):
    assert editor._vim.mode == MODE_NORMAL


def test_insert_enter_and_leave(editor):
    seen = []
    editor._vim.modeChanged.connect(seen.append)
    send(editor, 'i')
    assert editor._vim.mode == MODE_INSERT
    esc(editor)
    assert editor._vim.mode == MODE_NORMAL
    assert seen == [MODE_INSERT, MODE_NORMAL]


def test_esc_from_insert_moves_cursor_left(editor):
    load(editor, 'abc', 2)
    send(editor, 'i')
    esc(editor)
    assert pos(editor) == 1


def test_h_and_l_with_counts(editor):
    load(editor, 'abcdef')
    send(editor, '3l')
    assert pos(editor) == 3
    send(editor, '2h')
    assert pos(editor) == 1


def test_vertical_moves(editor):
    load(editor, 'abc\ndefgh\nij\n')
    send(editor, 'lljj')
    assert pos(editor) == 11
    send(editor, 'k')
    assert pos(editor) == 5


def test_dollar(editor):
    load(editor, 'abc\ndef\n', 5)
    send(editor, '$')
    assert pos(editor) == 6


def test_zero(editor):
    load(editor, 'abc\ndef\n', 5)
    send(editor, '0')
    assert pos(editor) == 4


def test_caret(editor):
    load(editor, '   abc\n', 6)
    send(editor, '^')
    assert pos(editor) == 3


def test_G_gg_and_count_G(editor):
    load(editor, 'aaa\nbbb\nccc\n')
    send(editor, 'G')
    assert pos(editor) == 8
    send(editor, 'gg')
    assert pos(editor) == 0
    send(editor, '2G')
    assert pos(editor) == 4


def test_return_moves_to_first_non_blank_of_next_line(editor):
    load(editor, '  aa\n  bb\n', 2)
    send(editor, '\n')
    assert pos(editor) == 7


def test_space_and_backspace(editor):
    load(editor, 'abc')
    send(editor, ' ')
    assert pos(editor) == 1
    send(editor, '\b')
    assert pos(editor) == 0
    send(editor, '\b')
    assert pos(editor) == 0


def test_esc_clears_count(editor):
    load(editor, 'abcdef')
    send(editor, '3')
    esc(editor)
    send(editor, 'l')
    assert pos(editor) == 1


def test_reset(editor):
    send(editor, '3')
    assert editor._vim.count == '3'
    editor._vim.reset()
    assert editor._vim.mode == MODE_NORMAL
    assert editor._vim.count == ''


def test_arrow_keys_pass_through(editor):
    load(editor, 'abcdef')
    send_key(editor, Qt.Key_Right)
    assert pos(editor) == 1


def test_tab_is_consumed(editor):
    load(editor, 'abc', 1)
    send(editor, '\t')
    assert editor.toPlainText() == 'abc'
    assert pos(editor) == 1


def test_unknown_normal_key_does_not_insert(editor):
    load(editor, 'abc', 1)
    send(editor, 'q')
    assert editor.toPlainText() == 'abc'
    assert pos(editor) == 1


def test_insert_mode_typing_passthrough(editor):
    load(editor, 'abc', 1)
    send(editor, 'i')
    send(editor, 'XY')
    assert editor.toPlainText() == 'aXYbc'
    assert pos(editor) == 3


def test_ctrl_bracket_enters_normal(editor):
    send(editor, 'i')
    send_key(editor, Qt.Key_BracketLeft, '\x1b', Qt.ControlModifier)
    assert editor._vim.mode == MODE_NORMAL
