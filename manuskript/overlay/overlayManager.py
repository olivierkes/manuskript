#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class OverlayManager:
    def __init__(self, overlay: Gtk.Overlay):
        self.overlay = overlay
        self.layers: list[Gtk.Widget] = []

    def add_layer(self, layer_widget: Gtk.Widget):
        """Add a new overlay layer."""
        self.overlay.add_overlay(layer_widget)
        self.layers.append(layer_widget)
        layer_widget.show_all()

    def remove_layer(self, layer_widget: Gtk.Widget):
        """Remove a layer."""
        if layer_widget in self.layers:
            self.overlay.remove(layer_widget)
            self.layers.remove(layer_widget)

    def hide_layers(self):
        for layer in self.layers:
            layer.hide()

    def show_layers(self):
        for layer in self.layers:
            layer.show()


    def clear_layers(self):
        """Remove all overlay layers."""
        for layer in list(self.layers):
            self.overlay.remove(layer)
        self.layers.clear()

    def reorder_layer(self, layer_widget: Gtk.Widget, index: int):
        """Change layer order."""
        if layer_widget not in self.layers:
            return

        self.layers.remove(layer_widget)
        self.layers.insert(index, layer_widget)

        for layer in self.layers:
            self.overlay.remove(layer)
            self.overlay.add_overlay(layer)
