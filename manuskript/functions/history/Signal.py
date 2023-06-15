
class Signal():
    def __init__(self) -> None:
        self._methods = []

    def connect(self, func):
        self._methods.append(func)
    
    def disconnect(self, func):
        try:
            self._methods.remove(func)
        except ValueError:
            raise TypeError
        
    def disconnect(self):
        if len(self._methods) == 0:
            raise TypeError
        self._methods.pop()

    def fire(self, data):
        for m in self._methods:
            m(data)

