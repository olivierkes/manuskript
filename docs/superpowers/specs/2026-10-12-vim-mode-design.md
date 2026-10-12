# Vim Mode for Manuskript — Design

Date: 2026-10-12
Status: Approved design; spec pending user review
Repo: `~/code/manuskript` (fork of `github.com/olivierkes/manuskript`, branch `develop`, baseline commit `01e0574`)
Goal: Personal-use MVP vim keybindings for Manuskript's prose editors. Run from source; pacman-installed 0.17.0 stays untouched.

## 1. Context

- Manuskript 0.17.0 (PyQt5; PyQt5 5.15.11 / Qt 5.15.18; Python 3.14 on this machine) has no vim mode. Upstream issue #829 requests it (open since 2021).
- Prior-art research (2026-10): FakeVim (C++/SIP bindings, build risk, compiled dependency), qutepart (Python vim engine tightly coupled to its own widget), Neovim embedding (architectural mismatch). All rejected for this MVP in favor of a self-contained module.
- Chosen: new pure-Python module `manuskript/ui/views/vimMode.py`, hooked into the prose editors only. No new dependencies.

## 2. Scope

### 2.1 Enabled surfaces (always-on)

| Surface | Widget | Creation site |
|---|---|---|
| Single-item prose editor | `MDEditView` (`txtRedacText`) | `editorWidget_ui.py:25`, enabled in `editorWidget.__init__` |
| Folder-continuous text view (one editor per child text item) | `MDEditView` | `editorWidget.py:194` (`addText`), enabled there |
| Fullscreen / distraction-free | `MDEditView` | `fullScreenEditor.py:39`, enabled there |

Each enabled editor instance starts in NORMAL mode; state is per-instance.

### 2.2 Explicitly excluded

Metadata fields (character/world/plot/summary — these are `MDEditCompleter` instances), card title editors (`addTitle`), cork/outline card views, theme preview (`themes.py:275`), and all other `textEditView` uses. Enablement is opt-in via `enableVim()`; no class-wide behavior change.

### 2.3 MVP command set (accepted)

- **Modes:** NORMAL, INSERT. `Esc`/`Ctrl-[` → NORMAL (from INSERT, and in NORMAL it clears pending state).
- **Motions:** `h j k l`, `w W b B e E`, `0 ^ $`, `gg G`, `f/t/F/T <char>` with `;`/`,` repeat. Counts compose (`3w`, `5j`).
- **Operators:** `d c y` + motion (`dw de dW dE db d0 d^ d$ dgg dG dh dj dk df<x> dt<x> ...`), `dd cc yy`, `D` (= `d$`), `C` (= `c$`).
- **Insert entry:** `i a I A o O` (each enters INSERT; `cc`/`C` end in INSERT as usual).
- **Other edits:** `x`, `r<char>`, `p`/`P`, `J` (join lines).
- **Undo:** `u`, `Ctrl-r` → native Qt undo/redo, grouped one undo step per vim command.
- **Indicator:** `-- NORMAL --` / `-- INSERT --`.

### 2.4 Deferred (explicit non-goals for MVP)

Visual mode, `/` search, text objects (`ciw`, `di"`, `da(`), `.` dot-repeat, named registers, macros, marks/jumplist, block cursor rendering, settings toggle, applying vim to metadata fields (would need `MDEditCompleter`/popup interplay).

## 3. Architecture

### 3.1 Module

`manuskript/ui/views/vimMode.py` — pure Python, PyQt5 only (estimated 700-1000 LOC):

- `VimMode(QObject)` — one instance per editor widget.
  - **State:** `mode` (NORMAL/INSERT), count buffer, pending operator (`d/c/y` + optional count), pending motion (awaiting char for `f/t/F/T`), last find (for `;`/`,`), unnamed register (text + linewise flag).
  - **Signal:** `modeChanged(str)`.
  - **Entry:** `handleKey(event) -> bool` — returns True when the event is consumed (event handling must stop); False lets the existing Qt path run.
  - **Lifecycle:** `reset()` — back to NORMAL, clear all pending state (on item switch).
- Cursor mechanics via `QTextCursor` on the widget's document. Normal-mode edits wrapped in `cursor.beginEditBlock()/endEditBlock()` → one undo step per command.

### 3.2 Key routing

Single guard at the top of `MDEditView.keyPressEvent`:

```python
def keyPressEvent(self, event):
    if self._vim is not None and self._vim.handleKey(event):
        return
    ...  # existing handling (Return/markdown continuation, Tab, textEditView)
```

- Enabled editors are plain `MDEditView` instances (no completer), so no popup interplay exists in MVP surfaces.
- **INSERT mode:** `handleKey` returns False for everything except `Esc`/`Ctrl-[`. Manuskript behavior is 100% untouched in insert mode: markdown list continuation (`handleCarriageReturn`), `Tab`, `Ctrl+V` clipboard override, spellcheck, typewriter scrolling, 500 ms `submit()` sync.
- **NORMAL mode:**
  - Consumes: printable keys, `Esc`, `Return` (moves to next line, first non-blank), `Backspace` (= `h`), `Space` (= `l`), `Delete` (= `x`), `Tab` (no-op).
  - Passes through: arrow keys / Home / End / PageUp / PageDown (native movement), and all `Ctrl`/`Alt`/`Meta` combinations **except** `Ctrl-[` (→ Esc) and `Ctrl-r` (→ redo).
  - Consumes `Ctrl+V` as a no-op (prevents the existing `textEditView` clipboard dump in normal mode; paste is `p`/`P`).
- Normal-mode navigation keys that move the cursor (arrows etc.) do not change mode or clear pending state.

### 3.3 Command semantics

- **Counts:** digits `1-9` accumulate; `0` is a motion when no count is pending. Counts apply to motions and operators (`d2w`, `3dd`, `2yy`, `2j`).
- **Operator + motion:** waits for a motion; operator count × motion count multiply like vim. Invalid combination cancels pending state silently. `Esc` cancels everything.
- **Linewise vs charwise:** `j k gg G` and doubled operators (`dd cc yy`) are linewise; `w e b h l 0 ^ $ f t` are charwise. Linewise operator selections include the full line(s) with line terminators.
- **Register:** single unnamed register. `d/c/x` and line ops fill it; `y` fills it. Linewise flag preserved so `p`/`P` paste linewise for `dd`/`yy`.
- **Paste:** linewise `p` inserts below current line, `P` above (cursor to first non-blank of pasted line); charwise `p` inserts after cursor, `P` before (cursor on last/first pasted char).
- **Undo:** `u`/`Ctrl-r` call `widget.undo()/redo()`; each normal-mode command is one edit block → one undo step. Insert-mode typing keeps native Qt grouping.
- **Cursor after command:** vim conventions — after `x`/`dw` cursor on first removed char; after `dd` on first non-blank of the line now at that position; `c` commands end in INSERT; `J` between the joined lines.
- **Empty-document / boundary motions:** clamp, never raise.
- **State reset:** `vim.reset()` whenever the editor switches item (`MDEditView.setCurrentModelIndex`), so new items start in NORMAL at a clean state.

## 4. Integration points (exact)

1. `manuskript/ui/views/textEditView.py`
   - `__init__`: `self._vim = None`.
   - New method `enableVim()`: lazily imports and instantiates `VimMode(self)` if not already enabled. (Lazy import avoids import cycles.)
2. `manuskript/ui/views/MDEditView.py`
   - Top of `keyPressEvent`: the guard (section 3.2).
   - `setCurrentModelIndex`: `if self._vim: self._vim.reset()`.
   - `focusInEvent`: if vim enabled, refresh the mode indicator (see below).
3. `manuskript/ui/editors/editorWidget.py`
   - `__init__` (after `setupUi`): `self.txtRedacText.enableVim()`.
   - `addText()` (folder-continuous view): `edt.enableVim()`.
4. `manuskript/ui/editors/fullScreenEditor.py`
   - After creating `self.editor`: `self.editor.enableVim()`.
   - Add a small mode `QLabel` to the existing bottom/top panel (styled like the word-count label), connected to `modeChanged`.
5. Mode indicator (main window)
   - Main window already owns `self.statusbar` (`mainWindow.py:1022`).
   - `vimMode.py` provides a tiny helper: on `modeChanged`, locate `self.window()`; if it exposes `statusBar()` (QMainWindow), lazily create/reuse one shared permanent `QLabel` on that window and set `-- NORMAL --` / `-- INSERT --`. Shared across the window's editors; refreshed on focus-in so the active editor's mode is shown.
   - No status bar is created where none exists (fullscreen uses its own label).

**No changes to:** model sync (`submit()` / 500 ms timer), `toIdealText`/NBSP handling, undo infrastructure, settings, highlighter, spellcheck.

## 5. Testing

### 5.1 Automated (`tests/`, new — repo has no test suite)

- `tests/conftest.py`: `QT_QPA_PLATFORM=offscreen` set before QApplication; session-scoped QApplication fixture.
- `tests/test_vim_mode.py`: instantiate `MDEditView` (no index), `enableVim()`, set document text, dispatch `QKeyEvent`s directly to `keyPressEvent` (and `QTest.keyClicks` where text payload matters). Assert document text, cursor position, and mode per case:
  - motions and counts (`w`, `3w`, `b`, `e`, `0`, `$`, `gg`, `G`, `f`/`t` with `;`/`,`)
  - operators: `dw`, `de`, `d$` (=`D`), `dd`, `2dd`, `cc`, `yy`+`p`/`P` (linewise), `yw`+`p` (charwise)
  - `x`, `r`, `J`, insert entries (`i a I A o O`) and that they land in INSERT
  - undo grouping: two commands → exactly two `undo()` steps
  - mode transitions: `Esc`, `Ctrl-[`; Esc clears pending count/operator
  - boundary no-ops on empty/single-line documents; invalid operator+motion cancels
  - insert passthrough: plain typing inserts, `Ctrl+V` still inserts clipboard (Qt path), `u` in insert does not trigger vim undo
- Run: `QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -q`.

### 5.2 Manual checklist

- `python3 bin/manuskript` from repo root; open existing project.
- Single-item editor: write a paragraph in INSERT (markdown list continuation works); NORMAL mode: motions, `ciw`-less edits (`dw`, `cc`), `u`/`Ctrl-r`, `p`.
- Folder-continuous text view: vim active per child editor; switching items resets to NORMAL.
- Fullscreen: indicator visible; write/edit; leave → re-enter.
- Persistence: make edits with vim, switch items, quit, reopen → changes saved (500 ms sync).
- Spellcheck, theme fonts/margins, typewriter scrolling unaffected.
- `Ctrl+C` copy, `Ctrl+Z` pass-through from NORMAL behave sanely.

## 6. Effort & sequence (≈3-4 days)

1. Baseline: run cloned `develop` from source; smoke-test (≈0.5 day).
2. `vimMode.py` core + unit tests (motions, counts, operators, edits, undo) (≈1.5-2 days).
3. Integration at the sites above + indicators + manual passes (≈1 day).
4. Edge polish + full verification (≈0.5 day).

## 7. Risks & limitations

- Linewise semantics across soft-wrapped lines: use `QTextBlock` boundaries, not visual lines (implementation care, covered by tests).
- Keyboard layout: commands match `event.key()`; with a non-Latin layout the same physical keys will not produce vim commands (matches default vim behavior; a future `langmap`-like option is out of scope).
- Python 3.14 + develop baseline: verify during step 1 (installed 0.17.0 runs, so risk is low).
- Undo granularity relies on Qt edit-block coalescing; validated by the undo-grouping tests.
