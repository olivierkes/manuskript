#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.plugin.abstractPlugin import AbstractPlugin

import importlib
import os
import pkgutil
import sys

__path__ = pkgutil.extend_path(__path__, __name__)

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from importlib.machinery import FileFinder, SourceFileLoader


def loadPlugins():
    plugins = []
    paths = []
    
    for importer in pkgutil.iter_importers():
        if not importer or type(importer) is not FileFinder:
            continue

        paths.append(os.path.join(importer.path, 'manuskript', 'plugin'))
    
    for module_info in pkgutil.iter_modules(paths):
        if not module_info or not module_info.ispkg:
            continue

        name = 'manuskript.plugin.' + module_info.name
        path = os.path.join(module_info.module_finder.path, module_info.name, '__init__.py')

        try:
            module = SourceFileLoader(name, path).load_module()
        except Exception:
            continue

        try:
            plugin_cls = module.Plugin
        except AttributeError:
            continue

        try:
            if not issubclass(plugin_cls, AbstractPlugin):
                continue

            plugin = plugin_cls()
        except TypeError:
            continue

        if not plugin:
            continue

        plugins.append(plugin)
    
    return plugins
