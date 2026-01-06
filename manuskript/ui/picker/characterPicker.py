from gi.repository import Gtk, GObject
from manuskript.data import Characters
from manuskript.data.color import Color
from manuskript.data.importance import Importance
from manuskript.ui.util import pixbufFromColor

class CharacterPicker(Gtk.Box):
    __gsignals__ = {
        "character-selected": (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    def __init__(self, button, characters: Characters):
        super().__init__()

        self.characters = characters

        self.store = Gtk.TreeStore(GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)

        self.currentImportanceFilter = None
        self.search_text = ""

        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self._filterCharacters)

        search = Gtk.SearchEntry()
        search.connect("search-changed", self._on_search_changed)

        header_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6
        )

        self.cssProvider = Gtk.CssProvider()
        self.cssProvider.load_from_data(b"""
            .highlighted-button {
                border: 2px solid #000000;
            }
        """)

        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), self.cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        btns = [("All", None)] + [(importance.name.capitalize(), importance) for importance in reversed(Importance)]

        for label, importance in btns:
            btn = Gtk.Button(label=label)

            if label == "All":
                btn.get_style_context().add_class('highlighted-button')
                self.last_clicked_btn = btn

            btn.connect(
                "clicked",
                lambda b, i=importance: self._onImportanceFilterSelect(b, i)
            )
            header_box.pack_start(btn, False, False, 0)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(6)

        box.pack_start(search, False, False, 0)
        box.pack_start(header_box, False, False, 0)

        scroller = self._buildCharacterGrid()
        box.pack_start(scroller, True, True, 0)

        self.popover = Gtk.Popover.new(button)
        self.popover.add(box)

        self._rebuildGrid()

    def _on_search_changed(self, entry):
        self.search_text = entry.get_text()
        self.filter.refilter()
        self._rebuildGrid()

    def _addCharacterToStore(self, character):
        category = character.importance
        self.store.append(None, [category, character])

    def _filterCharacters(self, model, iter_, data=None):
        category = model[iter_][0]
        character = model[iter_][1]

        if self.currentImportanceFilter != None and category != self.currentImportanceFilter:
            return False

        if self.search_text:
            return self.search_text.lower() in character.name.lower()

        return True

    def _buildCharacterGrid(self):
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_height(300)

        self.grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        scroller.add(self.grid)

        return scroller

    def _rebuildGrid(self):
        for child in self.grid.get_children():
            self.grid.remove(child)

        columns = 3
        row = col = 0

        iter_ = self.filter.get_iter_first()
        while iter_:
            character = self.filter[iter_][1]
            name = character.name
            color = character.color

            btn = Gtk.Button(label=name)

            btn = Gtk.Button()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

            pixbuf = pixbufFromColor(color)
            image = Gtk.Image.new_from_pixbuf(pixbuf)

            label = Gtk.Label(label=name)

            box.pack_start(image, False, False, 0)
            box.pack_start(label, True, True, 0)

            btn.add(box)
            btn.show_all()

            btn.connect("clicked", self._onCharacterClick, character)

            self.grid.attach(btn, col, row, 1, 1)

            col += 1
            if col >= columns:
                col = 0
                row += 1

            iter_ = self.filter.iter_next(iter_)

        self.grid.show_all()

    def _onCharacterClick(self, button, userdata):        
        self.emit("character-selected", userdata)
        self.popover.hide()

    def _setImportanceFilter(self, importance):
        self.currentImportanceFilter = importance
        self.filter.refilter()
        self._rebuildGrid()

    def _onImportanceFilterSelect(self, button, importance):
        if self.last_clicked_btn:
            self.last_clicked_btn.get_style_context().remove_class('highlighted-button')

        button.get_style_context().add_class('highlighted-button')
        self.last_clicked_btn = button
  
        self._setImportanceFilter(importance)

    def _clearStore(self):
        for row in self.store:
            self.store.remove(row.iter)
    
    def show(self, characters):
        self._clearStore()

        for character in self.characters:
            if not character.UID.value in characters:
                self._addCharacterToStore(character)

        self._setImportanceFilter(None)
        self.popover.show_all()
        self.popover.popup()