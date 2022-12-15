#!/usr/bin/env python
# --!-- coding: utf8 --!--

import subprocess
import pathlib
import importlib.util
import sys

# This is to produce an environment variable in GH Actions exclusively for use in CI/CD builds.


def writeVersionPlusHash() -> bool:
    """This function will permit us to rewrite
    the inline version.py file to contain the
    appropriate version-plus-hash-short to be
    shown in the about screen, version diagnostics
    and more.  This helps us better keep track
    of long-running issues in a relatively
    consise manner."""

    sha_short = (
        subprocess.run(
            "git rev-parse --short HEAD", shell=True, check=True, capture_output=True
        )
        .stdout.strip()
        .decode("utf-8")
    )  # UTF8 decode as it's a UTF8 situation.

    
    version_file = pathlib.Path("./manuskript/version.py").absolute()

    spec = importlib.util.spec_from_file_location(
        "manuskript.version", version_file.absolute()
    )
    temp = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = temp
    spec.loader.exec_module(temp)

    # used in final output.
    non_commit_version = temp.getVersion()

    # Used to rewrite the situation here.

    version_file_contents = open(str(version_file), 'r').readlines()

    for key, f in enumerate(version_file_contents):
        if ("__version__ = ") in f:
            version_file_contents[key] = f"__version__ = \"{non_commit_version}-{sha_short}\"\n"

    try:
        with open(str(version_file), 'w') as output_stub:
            output_stub.writelines(version_file_contents)
        return f"{non_commit_version}-{sha_short}"
    except:
        return None
        