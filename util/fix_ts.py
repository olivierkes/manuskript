#!/bin/python

import re
import sys

from lxml import etree


def main(argv) -> int:
    if len(argv) < 2:
        print("You need to specify a .ts file!")
        return 1

    path = argv[1]

    if (len(path) < 3) or (path[-3:] != ".ts"):
        print("Please specify a path to a .ts file!")
        return 2

    tree = None

    with open(path, "rb") as file:
        tree = etree.parse(file)

    if tree is None:
        print("Parsing failed!")
        return 3

    root = tree.getroot()
    if root.tag != "TS":
        print("Wrong type of file!")
        return 4

    for context in root.getchildren():
        if context.tag != "context":
            continue

        for message in context.getchildren():
            if message.tag != "message":
                continue

            source = message.find("source")
            translation = message.find("translation")

            if (source is None) or (translation is None):
                continue

            sourceText = etree.tostring(source, encoding="unicode").strip()

            if "&amp;" in sourceText:
                continue

            translationText = etree.tostring(translation, encoding="unicode").strip()
            translationText = re.sub(r"&amp;([a-zA-Z]+);", r"&\g<1>;", translationText)

            translationNode = etree.fromstring(translationText)
            translation.text = translationNode.text

    with open(path, "wb") as file:
        tree.write(file, encoding="utf-8", xml_declaration=True, pretty_print=True)

    print("Fixing finished!")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
