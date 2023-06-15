from manuskript.functions.history.NavigatedEvent import NavigatedEvent
from manuskript.functions.history.Signal import Signal


class History():
    def __init__(self) -> None:
        self._entries = []
        self._position = 0
        self.navigated = Signal()
        self._navigating = False

    def next(self, entry):
        if self._navigating:
            return

        while self._position < len(self._entries) - 1:
            self._entries.pop()
        
        self._entries.append(entry)
        self._position = len(self._entries) - 1
        self._navigating = True
        self.navigated.fire(NavigatedEvent(self._position, len(self._entries), entry))
        self._navigating = False

    
    def replace(self, entry):
        if self._navigating:
            return
    
        while self._position < len(self._entries):
            self._entries.pop()

        self._entries.append(entry)
        self._position = len(self._entries) - 1
        self._navigating = True
        self.navigated.fire(NavigatedEvent(self._position, len(self._entries), entry))
        self._navigating = False

    def forward(self):
        if self._position < len(self._entries) - 1:
            self._position += 1
            self._navigating = True
            self.navigated.fire(NavigatedEvent(self._position, len(self._entries), self._entries[self._position]))
            self._navigating = False

    def back(self):
        if self._position > 0:
            self._position -= 1
            self._navigating = True
            self.navigated.fire(NavigatedEvent(self._position, len(self._entries), self._entries[self._position]))
            self._navigating = False

    def reset(self):
        self._entries.clear()
        self._position = 0
        self.navigated.fire(NavigatedEvent(self._position, len(self._entries), None))
