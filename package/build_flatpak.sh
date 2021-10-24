#!/bin/sh
cd flatpak

# Generate config for python dependencies as modules:
flatpak-pip-generator lxml pyenchant pyspellchecker symspellpy markdown

# Build flatpak with all necessary modules:
flatpak-builder build-dir ch.theologeek.Manuskript.json --force-clean
