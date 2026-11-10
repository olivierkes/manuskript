from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent, QTextCursor
from PyQt5.QtWidgets import QMainWindow

from manuskript.ui.views.MDEditView import MDEditView
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


def test_counted_gg(editor):
    load(editor, '  aa\n  bb\n  cc\n', 11)
    send(editor, '2gg')
    assert pos(editor) == 7
    send(editor, '3gg')
    assert pos(editor) == 12


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


def test_word_motions(editor):
    load(editor, 'one, two three\nfour\n')
    send(editor, 'w')
    assert pos(editor) == 3
    send(editor, 'w')
    assert pos(editor) == 5
    send(editor, 'e')
    assert pos(editor) == 7
    send(editor, 'b')
    assert pos(editor) == 5
    send(editor, 'b')
    assert pos(editor) == 3


def test_big_word_motions(editor):
    load(editor, 'one, two three\nfour\n')
    send(editor, 'W')
    assert pos(editor) == 5
    send(editor, 'E')
    assert pos(editor) == 7
    send(editor, 'B')
    assert pos(editor) == 5


def test_count_word_motion(editor):
    load(editor, 'one two three four\n')
    send(editor, '2w')
    assert pos(editor) == 8


def test_find_char(editor):
    load(editor, 'hello world\n')
    send(editor, 'fo')
    assert pos(editor) == 4
    send(editor, ';')
    assert pos(editor) == 7
    send(editor, ',')
    assert pos(editor) == 4


def test_find_with_count(editor):
    load(editor, 'hello world\n')
    send(editor, '2fo')
    assert pos(editor) == 7


def test_till_char(editor):
    load(editor, 'hello world\n')
    send(editor, 'to')
    assert pos(editor) == 3


def test_find_backwards(editor):
    load(editor, 'hello world\n', 10)
    send(editor, 'Fo')
    assert pos(editor) == 7
    send(editor, ';')
    assert pos(editor) == 4


def test_till_backwards(editor):
    load(editor, 'hello world\n', 10)
    send(editor, 'To')
    assert pos(editor) == 8


def test_find_missing_char_does_not_move(editor):
    load(editor, 'hello world\n')
    send(editor, 'fz')
    assert pos(editor) == 0


def test_x_deletes_char(editor):
    load(editor, 'abcdef')
    send(editor, 'x')
    assert editor.toPlainText() == 'bcdef'
    assert pos(editor) == 0


def test_x_with_count(editor):
    load(editor, 'abcdef')
    send(editor, 'x')
    send(editor, '3x')
    assert editor.toPlainText() == 'ef'
    assert pos(editor) == 0


def test_delete_key_deletes_char(editor):
    load(editor, 'abcdef')
    send_key(editor, Qt.Key_Delete)
    assert editor.toPlainText() == 'bcdef'
    assert pos(editor) == 0


def test_replace_char(editor):
    load(editor, 'abcd', 1)
    send(editor, 'rZ')
    assert editor.toPlainText() == 'aZcd'
    assert pos(editor) == 1


def test_replace_with_count(editor):
    load(editor, 'abcd')
    send(editor, '2rZ')
    assert editor.toPlainText() == 'ZZcd'
    assert pos(editor) == 0


def test_join_lines(editor):
    load(editor, 'aa\nbb\ncc\n')
    send(editor, 'J')
    assert editor.toPlainText() == 'aa bb\ncc\n'
    assert pos(editor) == 2


def test_join_with_count(editor):
    load(editor, 'aa\nbb\ncc\n')
    send(editor, '2J')
    assert editor.toPlainText() == 'aa bb cc\n'


def test_append(editor):
    load(editor, 'abc', 1)
    send(editor, 'a')
    send(editor, 'X')
    assert editor.toPlainText() == 'abXc'
    assert pos(editor) == 3


def test_insert_at_first_non_blank(editor):
    load(editor, '  abc', 5)
    send(editor, 'I')
    send(editor, 'X')
    assert editor.toPlainText() == '  Xabc'


def test_append_at_end_of_line(editor):
    load(editor, 'abc')
    send(editor, 'A')
    send(editor, 'X')
    assert editor.toPlainText() == 'abcX'


def test_open_line_below(editor):
    load(editor, 'abc\ndef\n')
    send(editor, 'o')
    send(editor, 'X')
    assert editor.toPlainText() == 'abc\nX\ndef\n'


def test_open_line_above(editor):
    load(editor, 'abc')
    send(editor, 'O')
    send(editor, 'X')
    assert editor.toPlainText() == 'X\nabc'


def test_undo_after_x(editor):
    load(editor, 'abcdef')
    send(editor, 'x')
    assert editor.toPlainText() == 'bcdef'
    send(editor, 'u')
    assert editor.toPlainText() == 'abcdef'


def test_ctrl_r_redo(editor):
    load(editor, 'abcdef')
    send(editor, 'x')
    send(editor, 'u')
    send_key(editor, Qt.Key_R, '\x12', Qt.ControlModifier)
    assert editor.toPlainText() == 'bcdef'


def test_ctrl_v_consumed_in_normal(editor):
    from PyQt5.QtWidgets import QApplication
    QApplication.clipboard().setText('Q')
    load(editor, 'abc')
    send_key(editor, Qt.Key_V, '\x16', Qt.ControlModifier)
    assert editor.toPlainText() == 'abc'


def test_counted_join_is_single_undo(editor):
    load(editor, 'aa\nbb\ncc\n', 0)
    send(editor, '2J')
    assert editor.toPlainText() == 'aa bb cc\n'
    send(editor, 'u')
    assert editor.toPlainText() == 'aa\nbb\ncc\n'


def test_replace_with_space(editor):
    load(editor, 'abc', 2)
    send(editor, 'r ')
    assert editor.toPlainText() == 'ab '
    assert editor.textCursor().position() == 2
    send(editor, 'z')
    assert editor.toPlainText() == 'ab '


def test_dw(editor):
    load(editor, 'one two three\n')
    send(editor, 'dw')
    assert editor.toPlainText() == 'two three\n'
    assert pos(editor) == 0


def test_de(editor):
    load(editor, 'one two\n')
    send(editor, 'de')
    assert editor.toPlainText() == ' two\n'


def test_lD(editor):
    load(editor, 'abc def')
    send(editor, 'lD')
    assert editor.toPlainText() == 'a'


def test_llC(editor):
    load(editor, 'abc def')
    send(editor, 'llC')
    send(editor, 'X')
    esc(editor)
    assert editor.toPlainText() == 'abX'


def test_dd(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'dd')
    assert editor.toPlainText() == 'aa\ncc\n'
    assert pos(editor) == 3


def test_2dd(editor):
    load(editor, 'aa\nbb\ncc\ndd\n')
    send(editor, '2dd')
    assert editor.toPlainText() == 'cc\ndd\n'
    assert pos(editor) == 0


def test_yy_and_p_linewise(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'yy')
    assert editor._vim.register == 'bb\n'
    assert editor._vim.register_linewise is True
    send(editor, 'p')
    assert editor.toPlainText() == 'aa\nbb\nbb\ncc\n'
    assert pos(editor) == 6


def test_yy_and_P_linewise(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'yyP')
    assert editor.toPlainText() == 'aa\nbb\nbb\ncc\n'
    assert pos(editor) == 3


def test_yy_leaves_cursor_in_place(editor):
    load(editor, '  abc\n', 4)
    send(editor, 'yy')
    assert pos(editor) == 4
    assert editor._vim.register == '  abc\n'
    assert editor._vim.register_linewise is True


def test_yw_and_p_charwise(editor):
    load(editor, 'one two')
    send(editor, 'yw')
    assert editor._vim.register == 'one '
    send(editor, 'p')
    assert editor.toPlainText() == 'oone ne two'
    assert pos(editor) == 4


def test_cw(editor):
    load(editor, 'one two')
    send(editor, 'cw')
    assert editor._vim.mode == MODE_INSERT
    send(editor, 'X')
    esc(editor)
    assert editor.toPlainText() == 'X two'


def test_cc(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'cc')
    assert editor._vim.mode == MODE_INSERT
    send(editor, 'X')
    esc(editor)
    assert editor.toPlainText() == 'aa\nX\ncc\n'


def test_dj(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'dj')
    assert editor.toPlainText() == 'aa\n'


def test_dk(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'dk')
    assert editor.toPlainText() == 'cc\n'


def test_dG(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'dG')
    assert editor.toPlainText() == 'aa\n'


def test_dgg(editor):
    load(editor, 'aa\nbb\ncc\n', 3)
    send(editor, 'dgg')
    assert editor.toPlainText() == 'cc\n'


def test_operator_d2G(editor):
    load(editor, 'aa\nbb\ncc\ndd\n')
    send(editor, 'd2G')
    assert editor.toPlainText() == 'cc\ndd\n'


def test_operator_2dG(editor):
    load(editor, 'aa\nbb\ncc\ndd\n')
    send(editor, '2dG')
    assert editor.toPlainText() == 'cc\ndd\n'


def test_operator_counted_G_direction(editor):
    load(editor, 'aa\nbb\ncc\ndd\n', 6)
    send(editor, 'd2G')
    assert editor.toPlainText() == 'aa\ndd\n'


def test_operator_d2gg(editor):
    load(editor, 'aa\nbb\ncc\ndd\n', 6)
    send(editor, 'd2gg')
    assert editor.toPlainText() == 'aa\ndd\n'


def test_dtx(editor):
    load(editor, 'abcxdef')
    send(editor, 'dtx')
    assert editor.toPlainText() == 'xdef'


def test_2D(editor):
    load(editor, 'aa\nbb\ncc\n')
    send(editor, '2D')
    assert editor.toPlainText() == '\ncc\n'
    assert pos(editor) == 0


def test_2C(editor):
    load(editor, 'aa\nbb\ncc\n')
    send(editor, '2C')
    assert editor.toPlainText() == '\ncc\n'
    assert editor._vim.mode == MODE_INSERT
    assert pos(editor) == 0


def test_dFx(editor):
    load(editor, 'abcxdef', 6)
    send(editor, 'dFx')
    assert editor.toPlainText() == 'abc'


def test_d2fa(editor):
    load(editor, 'aabaa\n')
    send(editor, 'd2fa')
    assert editor.toPlainText() == 'a\n'
    assert pos(editor) == 0


def test_d2ta(editor):
    load(editor, 'aabaa\n')
    send(editor, 'd2ta')
    assert editor.toPlainText() == 'aa\n'


def test_d2Fa(editor):
    load(editor, 'aabaa\n', 4)
    send(editor, 'd2Fa')
    assert editor.toPlainText() == 'a\n'


def test_2dfa_uses_operator_count(editor):
    load(editor, 'aabaa\n')
    send(editor, '2dfa')
    assert editor.toPlainText() == 'a\n'


def test_c2fa_enters_insert(editor):
    load(editor, 'aabaa\n')
    send(editor, 'c2fa')
    assert editor._vim.mode == MODE_INSERT
    send(editor, 'X')
    esc(editor)
    assert editor.toPlainText() == 'Xa\n'


def test_undo_grouping(editor):
    load(editor, 'aa bb\ncc dd\n')
    send(editor, 'dw')
    assert editor.toPlainText() == 'bb\ncc dd\n'
    send(editor, 'dd')
    assert editor.toPlainText() == 'cc dd\n'
    send(editor, 'u')
    assert editor.toPlainText() == 'bb\ncc dd\n'
    send(editor, 'u')
    assert editor.toPlainText() == 'aa bb\ncc dd\n'


def test_enable_vim_is_idempotent(editor):
    vim = editor._vim
    editor.enableVim()
    assert editor._vim is vim


def test_main_window_status_label(qapp):
    win = QMainWindow()
    ed = MDEditView(win)
    ed.setEnabled(True)
    ed.enableVim()
    send(ed, 'i')
    assert win._vimModeLabel.text() == MODE_INSERT
    esc(ed)
    assert win._vimModeLabel.text() == MODE_NORMAL


def test_block_cursor_shown_in_normal(editor):
    load(editor, 'abc\ndef\n', 1)
    sels = editor.extraSelections()
    assert len(sels) == 1
    assert sels[0].cursor.selectionStart() == 1
    assert sels[0].cursor.selectionEnd() == 2
    assert editor.cursorWidth() == 0
    assert sels[0].format.background().color() == editor.palette().highlight().color()
    assert sels[0].format.foreground().color() == editor.palette().highlightedText().color()


def test_block_cursor_follows_motion_and_programmatic_move(editor):
    load(editor, 'abcdef', 0)
    send(editor, 'l')
    assert editor.extraSelections()[0].cursor.selectionStart() == 1
    assert editor.extraSelections()[0].cursor.selectionEnd() == 2
    c = QTextCursor(editor.document())
    c.setPosition(4)
    editor.setTextCursor(c)
    assert editor.extraSelections()[0].cursor.selectionStart() == 4
    assert editor.extraSelections()[0].cursor.selectionEnd() == 5


def test_block_cursor_cleared_in_insert(editor):
    load(editor, 'abc', 1)
    send(editor, 'i')
    send(editor, 'X')
    assert editor.extraSelections() == []
    assert editor.cursorWidth() == 1


def test_block_cursor_restored_after_esc(editor):
    load(editor, 'abc', 1)
    send(editor, 'i')
    esc(editor)
    assert len(editor.extraSelections()) == 1
    assert editor.extraSelections()[0].cursor.selectionStart() == 0
    assert editor.extraSelections()[0].cursor.selectionEnd() == 1
    assert editor.cursorWidth() == 0


def test_block_cursor_at_line_end_and_document_end(editor):
    load(editor, 'abc\ndef\n', 3)
    assert editor.extraSelections() == []
    assert editor.cursorWidth() == editor.fontMetrics().horizontalAdvance(' ')
    c = QTextCursor(editor.document())
    c.setPosition(8)
    editor.setTextCursor(c)
    assert editor.extraSelections() == []
    assert editor.cursorWidth() == editor.fontMetrics().horizontalAdvance(' ')


def test_block_cursor_after_reset(editor):
    load(editor, 'abcdef', 2)
    send(editor, 'i')
    assert editor.extraSelections() == []
    editor._vim.reset()
    assert len(editor.extraSelections()) == 1
    assert editor.extraSelections()[0].cursor.selectionStart() == 2
    assert editor.extraSelections()[0].cursor.selectionEnd() == 3
    assert editor.cursorWidth() == 0
