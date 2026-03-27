#!/usr/bin/env python3
"""
260327 virtualkss
thanks to vscode's claude haiku.

python calvin_table_customize.py calvin_env/data/calvin_table_D 20 --overwrite --verbose \
  --scene-template calvin_env/conf/scene/calvin_scene_D_custom.yaml \
  --config-template calvin_env/conf/config_data_collection_custom.yaml

"""
"""Clone and recolor a Calvin table dataset under multiple HSV hues.

Usage:
    python calvin_table_customize.py <source_table_dir> <num_colors> [options]

Example:
    python calvin_table_customize.py reference/RoboVLMs/calvin/calvin_env/data/calvin_table_D 4 \
        --scene-template reference/RoboVLMs/calvin/calvin_env/conf/scene/calvin_scene_D_custom.yaml \
        --config-template reference/RoboVLMs/calvin/calvin_env/conf/config_data_collection_custom.yaml

This creates:
    .../data/calvin_table_D_custom_00, ..._01 etc
    .../conf/scene/calvin_scene_D_custom_00.yaml etc
    .../conf/config_data_collection_custom_00.yaml etc

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

    p.add_argument("--scene-template", type=Path, default=None,
                   help="Optional scene yaml template to clone and patch table path")
    p.add_argument("--scene-output-dir", type=Path, default=None,
                   help="Directory to save generated scene yaml files (default: same as template)")
    p.add_argument("--config-template", type=Path, default=None,
                   help="Optional config yaml template to clone and patch scene name")
    p.add_argument("--config-output-dir", type=Path, default=None,
                   help="Directory to save generated config yaml files (default: same as template)")

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


def patch_scene_file(template_path: Path, output_path: Path, src_folder_name: str, dst_folder_name: str,
                     src_scene_name: str = None, dst_scene_name: str = None, verbose: bool = False):
    content = template_path.read_text(encoding="utf-8")
    content = content.replace(f"{src_folder_name}/", f"{dst_folder_name}/")
    if src_scene_name and dst_scene_name:
        content = content.replace(src_scene_name, dst_scene_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    if verbose:
        print(f"[INFO] Written scene config: {output_path}")


def patch_config_file(template_path: Path, output_path: Path, src_scene_name: str, dst_scene_name: str,
                      verbose: bool = False):
    content = template_path.read_text(encoding="utf-8")
    content = content.replace(f"- scene: {src_scene_name}", f"- scene: {dst_scene_name}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    if verbose:
        print(f"[INFO] Written config file: {output_path}")


def main():
    args = parse_args()
    source = args.source
    num_colors = args.num_colors
    overwrite = args.overwrite
    verbose = args.verbose
    scene_template = args.scene_template
    scene_output_dir = args.scene_output_dir
    config_template = args.config_template
    config_output_dir = args.config_output_dir

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
    source_base = source.name

    if scene_template and not scene_template.exists():
        print(f"Error: scene template does not exist: {scene_template}")
        sys.exit(1)

    if config_template and not config_template.exists():
        print(f"Error: config template does not exist: {config_template}")
        sys.exit(1)

    if scene_output_dir is None and scene_template is not None:
        scene_output_dir = scene_template.parent

    if config_output_dir is None and config_template is not None:
        config_output_dir = config_template.parent

    scene_template_name = None
    if scene_template:
        scene_template_name = scene_template.stem

    config_template_name = None
    if config_template:
        config_template_name = config_template.stem

    for idx in range(num_colors):
        if num_colors == 1:
            dest_name = f"{source_base}_custom"
            scene_name = scene_template_name if scene_template_name else None
            config_name = config_template_name if config_template_name else None
        else:
            dest_name = f"{source_base}_custom_{idx}"
            if scene_template_name:
                scene_name = f"{scene_template_name}_{idx}"
            else:
                scene_name = None
            if config_template_name:
                config_name = f"{config_template_name}_{idx}"
            else:
                config_name = None

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

        if scene_template and scene_name:
            dst_scene_path = scene_output_dir / f"{scene_name}.yaml"
            patch_scene_file(
                scene_template,
                dst_scene_path,
                src_folder_name=source_base,
                dst_folder_name=dest_name,
                src_scene_name=scene_template_name,
                dst_scene_name=scene_name,
                verbose=verbose,
            )

        if config_template and config_name and scene_name:
            dst_config_path = config_output_dir / f"{config_name}.yaml"
            patch_config_file(
                config_template,
                dst_config_path,
                src_scene_name=scene_template_name,
                dst_scene_name=scene_name,
                verbose=verbose,
            )

        if verbose:
            print(f"[OK] Generated {destination} with hue {hue:.1f}")

    print(f"Done: generated {num_colors} variants for {source}.")


if __name__ == "__main__":
    main()
