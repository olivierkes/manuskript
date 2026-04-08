#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class OverlayManager:
    def __init__(self, overlay: Gtk.Overlay):
        self.overlay = overlay
        self.layers: list[Gtk.Widget] = []

    def addLayer(self, layer_widget: Gtk.Widget):
        self.overlay.add_overlay(layer_widget)
        self.layers.append(layer_widget)
        layer_widget.show_all()

    def removeLayer(self, layerWidget: Gtk.Widget):
        if layerWidget in self.layers:
            self.overlay.remove(layerWidget)
            self.layers.remove(layerWidget)

    def hideLayers(self):
        for layer in self.layers:
            layer.hide()

    def showLayers(self):
        for layer in self.layers:
            layer.show()

    def clearLayers(self):
        for layer in list(self.layers):
            self.overlay.remove(layer)
        self.layers.clear()

    def reorderLayer(self, layer_widget: Gtk.Widget, index: int):
        if layer_widget not in self.layers:
            return

        self.layers.remove(layer_widget)
        self.layers.insert(index, layer_widget)

        for layer in self.layers:
            self.overlay.remove(layer)
            self.overlay.add_overlay(layer)
