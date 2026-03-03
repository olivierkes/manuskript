#!/usr/bin/env python
# --!-- coding: utf8 --!--

from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
from typing import Any

class Signals:
    _instance = None
    _initialized = False
    _initAllowed = False

    def __init__(self) -> None:
        if not Signals._initAllowed:
            raise Exception("Please use getUniqueInstance")
        
        self.callbacks: dict[str, list[Callable[[Any], None]]] = defaultdict(list)
        Signals._initialized = True

    @classmethod
    def getCommonInstance(cls) -> Signals:
        if cls._instance is None:
            cls._initAllowed = True
            cls._instance = cls()
            cls._initAllowed = False

        return cls._instance

    def connect(self, signal: str, callback: Callable[[Any], None]) -> None:
        self.callbacks[signal.lower()].append(callback)

    def emit(self, signal: str, *userData: Any) -> None:
        for callback in self.callbacks.get(signal.lower(), []):
            callback(*userData)

    def clear(self) -> None:
        self.callbacks.clear()
