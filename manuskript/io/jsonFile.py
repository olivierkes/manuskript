#!/usr/bin/env python
# --!-- coding: utf8 --!--

import json
from typing import Any

from manuskript.io.textFile import TextFile


class JsonFile(TextFile):
    def load(self) -> Any:
        return json.loads(TextFile.load(self))

    def save(self, content: Any) -> None:
        TextFile.save(self, json.dumps(content, indent=4, sort_keys=True))
