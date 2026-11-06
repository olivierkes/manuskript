#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.importer.abstractImporter import AbstractImporter
from manuskript.importer.markdownImporter import MarkdownImporter


__importers__ = [
    MarkdownImporter()
]


def getImporters() -> filter[AbstractImporter]:
    global __importers__
    return filter(lambda importer: importer.isValid(), __importers__)


def getImporterByFormat(inputFormat: str) -> AbstractImporter | None:
    for importer in getImporters():
        if importer.importFormat == inputFormat:
            return importer

    return None


def getImporterByName(name: str) -> AbstractImporter | None:
    for importer in getImporters():
        if importer.getName() == name:
            return importer

    return None


def registerImporter(importer: AbstractImporter) -> bool:
    global __importers__

    if not importer.isValid():
        return False

    if importer in __importers__:
        return False

    __importers__.append(importer)
    return True


def unregisterImporter(importer: AbstractImporter) -> bool:
    global __exporters__

    if not importer in __importers__:
        return False

    __importers__.remove(importer)
    return True
