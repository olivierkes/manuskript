# -*- mode: python -*-

block_cipher = None

# This is the spec file to be run with pyinstaller.
# However, it's what amounts to a python script, so
# we can do some incredibly cursed things to make 
# sure it builds, and the way we want it to.

# For some reason we need to explicitly include the current directory.  Unsure why.
import os
import sys
file_dir = os.path.dirname(".")
sys.path.append(file_dir)

# We're grabbing the current git SHA short to use in the version.

from util.hashed_version import writeVersionPlusHash

version = writeVersionPlusHash()

a = Analysis(
    ["bin/manuskript"],
    pathex=["."],
    binaries=None,
    datas=[
        ("icons", "icons"),
        ("libs", "libs"),
        ("resources", "resources"),
        ("sample-projects", "sample-projects"),
        ("i18n", "i18n"),
    ],
    hiddenimports=["xml.dom"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="manuskript",
    debug=False,
    strip=False,
    upx=True,
    console=True,
    icon=os.path.join(SPECPATH, "icons/Manuskript/manuskript.ico"),
)

wexe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="manuskriptw",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(SPECPATH, "icons/Manuskript/manuskript.ico"),
)

coll = COLLECT(
    exe, wexe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="manuskript"
)

app = BUNDLE(
    coll,
    name="manuskript.app",
    icon=os.path.join(SPECPATH, "icons/Manuskript/Manuskript.icns"),
    bundle_identifier="ch.theologeek.manuskript",
    version=version,
    info_plist={
        "NSPrincipalClass": "NSApplication",
        "NSAppleScriptEnabled": False,
        "NSHighResolutionCapable": True,
        "CFBundleURLTypes": [
            {
                "CFBundleURLName": "MSK",
                "CFBundleTypeRole": "Editor",
                "CFBundleURLSchemes": ["msk"],
            }
        ],
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "MSK",
                "CFBundleTypeIconFile": "icons/Manuscript/manuskript",
                "CFBundleTypeExtensions": ["msk"],
                "CFBundleTypeRole": "Editor",
                "LSHandlerRank": "Owner",
            }
        ],
    },
)
