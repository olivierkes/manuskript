#! /usr/bin/env python3
 
import sys
sys.path.insert(1, "/app/lib/manuskript")
print(sys.version)

# for debugging only
import PyQt5.QtWebEngineWidgets as webengine
print(webengine)

from manuskript import main
main.run()
