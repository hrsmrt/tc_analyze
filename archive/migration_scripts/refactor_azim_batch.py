#!/usr/bin/env python3
"""
Comprehensive batch refactoring script for azim_mean directory files.
Handles all variations of the old setting.json loading pattern.
"""

import os
import re
from pathlib import Path
from typing import Tuple

def refactor_file(filepath: Path) -> bool:
    """Refactor a single file. Returns True if changes were made."""

    print(f"Processing: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Check if already refactored
    if 'from utils.config import AnalysisConfig' in content:
        print(f"  → Already refactored, skipping")
        return False

    # Step 1: Remove old imports and paths
    content = re.sub(r'^script_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^sys\.path\.append\(os\.path\.normpath\(os\.path\.join\(script_dir, ".+"\)\)\)\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^# 実行ファイル（この\.pyファイル）を基準に相対パスを指定\n', '', content, flags=re.MULTILINE)

    # Step 2: Replace old setting.json block
    # Pattern 1: With comment
    old_pattern_1 = r'''# ファイルを開いてJSONを読み込む\nwith open\('setting\.json', 'r', encoding='utf-8'\) as f:\n    setting = json\.load\(f\)\nglevel = setting\['glevel'\]\nnt = setting\['nt'\]\ndt = setting\['dt_output'\]\ndt_hour = int\(dt / 3600\)\ntriangle_size = setting\['triangle_size'\]\nnx = 2 \*\* glevel\nny = 2 \*\* glevel\nnz = 74\nx_width = triangle_size\ny_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5\ndx = x_width / nx\ndy = y_width / ny\ninput_folder = setting\['input_folder'\]\nn_jobs = setting\.get\("n_jobs", 1\)'''

    # Pattern 2: Without comment, different formatting
    old_pattern_2 = r'''with open\('setting\.json', 'r', encoding='utf-8'\) as f:\n    setting = json\.load\(f\)\n\nglevel = setting\['glevel'\]\nnt = setting\['nt'\]\ndt = setting\['dt_output'\]\ndt_hour = int\(dt / 3600\)\ntriangle_size = setting\['triangle_size'\]\nnx = 2 \*\* glevel\nny = 2 \*\* glevel\nnz = 74\nx_width = triangle_size\ny_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5\ndx = x_width / nx\ndy = y_width / ny\ninput_folder = setting\['input_folder'\]\nn_jobs = setting\.get\("n_jobs", 1\)'''

    is_plot_file = '_plot' in filepath.name

    if is_plot_file:
        new_imports = '''from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()'''
    else:
        new_imports = '''from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)'''

    # Try pattern 1
    if re.search(old_pattern_1, content):
        content = re.sub(old_pattern_1, new_imports, content)
    # Try pattern 2
    elif re.search(old_pattern_2, content):
        content = re.sub(old_pattern_2, new_imports, content)
    else:
        # Try a more flexible pattern
        old_pattern_flex = r'''with open\('setting\.json'[^\n]+\n\s+setting = json\.load\(f\)[^\n]+\n[^\n]*\nglevel = setting\['glevel'\][^\n]+\nnt = setting\['nt'\][^\n]+\ndt = setting\['dt_output'\][^\n]+\ndt_hour = int\(dt / 3600\)[^\n]+\ntriangle_size = setting\['triangle_size'\][^\n]+\nnx = 2 \*\* glevel[^\n]*\nny = 2 \*\* glevel[^\n]*\nnz = 74[^\n]*\nx_width = triangle_size[^\n]*\ny_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5[^\n]*\ndx = x_width / nx[^\n]*\ndy = y_width / ny[^\n]*\ninput_folder = setting\['input_folder'\][^\n]*\nn_jobs = setting\.get\("n_jobs", 1\)'''
        content = re.sub(old_pattern_flex, new_imports, content)

    # Step 3: Handle style argument parsing for plot files
    if is_plot_file and 'sys.argv' in content:
        # Find style argument index
        style_match = re.search(r'sys\.argv\[(\d+)\]', content)
        if style_match:
            arg_index = style_match.group(1)

            # Replace old style block
            old_style = rf'''if len\(sys\.argv\) > {arg_index}:\n    mpl_style_sheet = sys\.argv\[{arg_index}\]\n    print\(f"Using style: \{{mpl_style_sheet\}}"\)\nelse:\n    print\("No style sheet specified, using default\."\)'''
            new_style = f'mpl_style_sheet = parse_style_argument(arg_index={arg_index})'
            content = re.sub(old_style, new_style, content)

    # Step 4: Replace variable references
    replacements = {
        r'\bnx\b': 'config.nx',
        r'\bny\b': 'config.ny',
        r'\bnz\b': 'config.nz',
        r'\bnt\b': 'config.nt',
        r'\bdt_hour\b': 'config.dt_hour',
        r'\bdx\b': 'config.dx',
        r'\bdy\b': 'config.dy',
        r'\bx_width\b': 'config.x_width',
        r'\by_width\b': 'config.y_width',
        r'\binput_folder\b': 'config.input_folder',
        r'\bn_jobs\b': 'config.n_jobs',
    }

    for old_var, new_var in replacements.items():
        content = re.sub(old_var, new_var, content)

    # Step 5: Replace grid coordinate generation for calc files
    if not is_plot_file:
        # Replace the x, y, X, Y generation
        grid_pattern = r'''# 格子点座標（m単位）\nx = \(np\.arange\(config\.nx\) \+ 0\.5\) \* config\.dx\ny = \(np\.arange\(config\.ny\) \+ 0\.5\) \* config\.dy\nX, Y = np\.meshgrid\(x, y\)'''
        grid_replacement = 'X, Y = grid.X, grid.Y'
        content = re.sub(grid_pattern, grid_replacement, content)

    # Step 6: Replace vgrid_filepath if present
    content = re.sub(r"setting\['vgrid_filepath'\]", "config.vgrid_filepath", content)
    content = re.sub(r'f"\{setting\[\'vgrid_filepath\'\]\}"', 'config.vgrid_filepath', content)

    # Step 7: Replace time_list calculation
    content = re.sub(
        r'time_list = \[t \* config\.dt_hour for t in range\(config\.nt\)\]',
        'time_list = config.time_list',
        content
    )

    # Step 8: Remove json import if no longer needed
    if 'json.load' not in content and 'json.dump' not in content:
        content = re.sub(r'^import json\n', '', content, flags=re.MULTILINE)

    # Step 9: Clean up empty lines (max 2 consecutive)
    content = re.sub(r'\n\n\n+', '\n\n', content)

    # Check if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Refactored successfully")
        return True
    else:
        print(f"  → No changes needed")
        return False


def main():
    """Main function to refactor all files."""
    azim_mean_dir = Path("azim_mean")

    if not azim_mean_dir.exists():
        print(f"Error: Directory '{azim_mean_dir}' not found")
        print(f"Current directory: {os.getcwd()}")
        return

    # Get all Python files
    py_files = sorted(azim_mean_dir.rglob("*.py"))

    print(f"Found {len(py_files)} Python files")
    print("=" * 60)
    print()

    refactored_count = 0
    skipped_count = 0

    for py_file in py_files:
        if refactor_file(py_file):
            refactored_count += 1
        else:
            skipped_count += 1
        print()

    print("=" * 60)
    print(f"Summary:")
    print(f"  Total files: {len(py_files)}")
    print(f"  Refactored: {refactored_count}")
    print(f"  Skipped: {skipped_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
