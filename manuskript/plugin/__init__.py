#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.plugin.abstractPlugin import AbstractPlugin
from manuskript.plugin.component import PluginComponent as Component

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


def findPlugins():
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
        except Exception as e:
            print("MODULE ERROR: ( " + name + ", " + path + " )" + str(e))
            continue

        try:
            plugin_cls = module.Plugin
        except AttributeError as e:
            print("MODULE ERROR: ( " + name + ", " + path + " )" + str(e))
            continue

        try:
            if not issubclass(plugin_cls, AbstractPlugin):
                continue

            plugin = plugin_cls()
        except TypeError as e:
            print("MODULE ERROR: ( " + name + ", " + path + " )" + str(e))
            continue

        if not plugin:
            continue

        plugins.append(plugin)
    
    return plugins


def loadPlugins(plugins: list[AbstractPlugin]) -> int:
    components = [e for e in Component]

    plugin_list: list[AbstractPlugin] = list(plugin for plugin in plugins)

    for component in components:
        for plugin in plugin_list:
            if plugin.loadComponent(component):
                plugin.loaded[component.value] = True
        
        plugin_list = list(filter(lambda plugin: plugin.loaded[component.value], plugin_list))
    
    if len(plugin_list) < len(plugins):
        unloadPlugins(list(filter(lambda plugin: not plugin.isValid(), plugins)))

    return len(plugin_list)


def unloadPlugins(plugins: list[AbstractPlugin]) -> int:
    components = [e for e in Component]
    components.reverse()

    for component in components:
        for plugin in plugins:
            if not plugin.loaded[component.value]:
                continue

            if plugin.unloadComponent(component):
                plugin.loaded[component.value] = False
    
    failed: int = 0

    for plugin in plugins:
        if True in plugin.loaded:
            failed += 1
    
    return len(plugins) - failed
