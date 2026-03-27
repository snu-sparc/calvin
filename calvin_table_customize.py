#!/usr/bin/env python3
"""
260327 virtualkss thanks to vscode's claude haiku
"""
"""Clone and recolor a Calvin table dataset under multiple HSV hues.

Usage:
    python calvin_table_customize.py <source_table_dir> <num_colors>

Example:
    python calvin_table_customize.py reference/RoboVLMs/calvin/calvin_env/data/calvin_table_D 4

This creates:
    reference/RoboVLMs/calvin/calvin_env/data/calvin_table_D_custom_00
    reference/RoboVLMs/calvin/calvin_env/data/calvin_table_D_custom_01
    reference/RoboVLMs/calvin/calvin_env/data/calvin_table_D_custom_02
    reference/RoboVLMs/calvin/calvin_env/data/calvin_table_D_custom_03

Each copy has its textures recolored with a single hue from an equally spaced HSV wheel.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow is required for this script. Install with: pip install pillow")

import colorsys


def parse_args():
    p = argparse.ArgumentParser(description="Clone and recolor calvin_table variants")
    p.add_argument("source", type=Path, help="Source calvin_table path (e.g. .../calvin_table_D)")
    p.add_argument("num_colors", type=int, help="Number of hue variants to generate (e.g., 3,4,6)")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing output folders")
    p.add_argument("--verbose", action="store_true", help="Print extra logging")
    return p.parse_args()


def recolor_texture(file_path: Path, hue_deg: float, verbose: bool = False):
    if verbose:
        print(f"Recoloring {file_path} -> hue={hue_deg:.1f}")

    im = Image.open(file_path).convert("RGBA")
    arr = im.load()
    w, h = im.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = arr[x, y]
            if a == 0:
                continue

            fr, fg, fb = r / 255.0, g / 255.0, b / 255.0
            h_old, s_old, v_old = colorsys.rgb_to_hsv(fr, fg, fb)
            h_new = (hue_deg % 360) / 360.0
            nr, ng, nb = colorsys.hsv_to_rgb(h_new, s_old, v_old)

            arr[x, y] = (
                int(round(nr * 255)),
                int(round(ng * 255)),
                int(round(nb * 255)),
                a,
            )

    im.save(file_path)


def main():
    args = parse_args()
    source = args.source
    num_colors = args.num_colors
    overwrite = args.overwrite
    verbose = args.verbose

    if not source.exists() or not source.is_dir():
        print(f"Error: source folder does not exist: {source}")
        sys.exit(1)

    textures_dir = source / "textures"
    if not textures_dir.exists() or not textures_dir.is_dir():
        print("Error: source folder should contain a textures/ subfolder")
        sys.exit(1)

    if num_colors < 1:
        print("Error: num_colors must be >= 1")
        sys.exit(1)

    parent = source.parent
    base = source.name

    for idx in range(num_colors):
        dest_name = f"{base}_{idx}"

        destination = parent / dest_name

        if destination.exists():
            if overwrite:
                if verbose:
                    print(f"[INFO] Removing existing folder: {destination}")
                shutil.rmtree(destination)
            else:
                print(f"Error: destination already exists: {destination}. Use --overwrite to replace.")
                sys.exit(1)

        if verbose:
            print(f"[INFO] Copying {source} -> {destination}")

        shutil.copytree(source, destination)

        hue = (idx * 360.0) / max(num_colors, 1)

        target_textures = destination / "textures"
        for tex_path in target_textures.iterdir():
            if not tex_path.is_file():
                continue
            if tex_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
                continue
            recolor_texture(tex_path, hue, verbose=verbose)

        if verbose:
            print(f"[OK] Generated {destination} with hue {hue:.1f}")

    print(f"Done: generated {num_colors} variants for {source}.")


if __name__ == "__main__":
    main()
