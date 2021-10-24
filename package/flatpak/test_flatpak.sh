#!/bin/sh
flatpak-builder --user --install --force-clean build-dir ch.theologeek.Manuskript.json
flatpak run ch.theologeek.Manuskript
