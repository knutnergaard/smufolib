#!/usr/bin/env python3

"""Migration script for font files created in SMufoLib v0.3.x or earlier.

This script addresses the issue of the lib keys created by the library not following
the UFO specification. Earlier "private" key names are changed to reverse-DNS
equivalents (i.e., ``'_name'`` -> ``'com.smufolib.name'``).

The script allows batch processing of multiple font files or directories containing
font files.

"""

from __future__ import annotations
from typing import Any
import os
import glob
import argparse
import time

from tqdm import tqdm

from smufolib import Font

PRIVATE_KEYS = {
    "_classes",
    "_designSize",
    "_description",
    "_engravingDefaults",
    "_name",
    "_names",
    "_sizeRange",
    "_spaces",
}


def rename_keys(lib: dict[str, Any]) -> None:
    """Rename keys in the given lib."""
    for key in list(lib.keys()):
        if key in PRIVATE_KEYS:
            lib[f"com.smufolib.{key[1:]}"] = lib.pop(key)


def process_font(path: str) -> None:
    """Process a single font file, updating lib keys."""
    try:
        print(f"Processing: {path}")
        font = Font(path)
        ticks = len(font)
        rename_keys(font.lib)

        with tqdm(total=ticks) as progressBar:
            for glyph in font:
                rename_keys(glyph.lib)
                progressBar.update(1)
                time.sleep(0.0001)

            font.save()
    except Exception as e:
        print(f"Error processing {path}: {e}")


def expand_paths(paths: list[str]) -> list[str]:
    """Expand directories into UFO font files."""
    fonts = []
    for path in paths:
        if os.path.isdir(path):
            fonts.extend(glob.glob(os.path.join(path, "*.ufo")))
        else:
            fonts.append(path)
    return fonts


def main(paths: list[str]) -> None:
    """Update UFO font and glyph lib keys."""
    for path in expand_paths(paths):
        process_font(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Please backup your files before running this script.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="list of paths to UFO font files or directories containing UFO font files",
    )
    args = parser.parse_args()
    print("Starting...")
    main(args.paths)
    print("Done.")
