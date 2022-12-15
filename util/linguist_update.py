#!/bin/python

import argparse
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(
    description="Update all QM source translation binaries based on the source .ts files."
)
parser.add_argument(
    "--binpath", type=str, help="Path to the lrelease binary.", required=True
)
parser.add_argument(
    "--transpath",
    type=str,
    help="Path to the source translations directory.  Does not recurse.",
    default="./i18n/",
)


def cleanupFiles(binpath, transpath) -> None:
    # Catch for if the user doesn't pass in a path but we're still passing a None.
    src_files = Path(transpath) if transpath is not None else "./i18n/"
    src_files = [
        x for x in src_files.iterdir() if x.is_file() and str(x).endswith(".qm")
    ]

    for file in src_files:
        # lrelease.exe path_to_translation.qm
        subprocess.run([lrelease_path, str(file)])


# This permits us to import these steps discretely for a bigger build tool.
if __name__ == "__main__":
    arguments = parser.parse_args()

    # To permit calling as a normal function too ig.
    if arguments.binpath is not None:
        lrelease_path = Path(arguments.binpath)
    if arguments.transpath is not None:
        trans_path = Path(arguments.transpath)

    cleanupFiles(lrelease_path, trans_path)
