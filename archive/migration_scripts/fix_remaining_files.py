#!/usr/bin/env python3
"""
Fix remaining files with incomplete setting blocks.
"""

import re
from pathlib import Path


def fix_incomplete_setting_block(filepath: Path) -> bool:
    """Fix files with incomplete setting blocks."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Check if it still has the old pattern
    if "with open('setting.json'" not in content:
        return False

    # Check if config is already imported
    if "from utils.config import AnalysisConfig" in content:
        return False

    is_plot_file = "_plot" in filepath.name

    # Pattern for incomplete setting block (various versions)
    patterns = [
        # Pattern with comment
        r"""# ファイルを開いてJSONを読み込む\nwith open\('setting\.json'[^\n]+\n[^\n]+\nglevel = setting\['glevel'\][^\n]+\nconfig\.nt = setting\['config\.nt'\][^\n]+\ndt = setting\['dt_output'\][^\n]+\nconfig\.dt_hour = int\(dt / 3600\)[^\n]+\ntriangle_size = setting\['triangle_size'\][^\n]+\nconfig\.n_jobs = setting\.get\("config\.n_jobs", 1\)[^\n]+\nconfig\.nx = 2 \*\* glevel[^\n]+\nconfig\.x_width = triangle_size[^\n]+\nconfig\.dx = config\.x_width / config\.nx""",
        # Pattern without comment
        r"""with open\('setting\.json'[^\n]+\n[^\n]+\nglevel = setting\['glevel'\][^\n]+\nconfig\.nt = setting\['config\.nt'\][^\n]+\ndt = setting\['dt_output'\][^\n]+\nconfig\.dt_hour = int\(dt / 3600\)[^\n]+\ntriangle_size = setting\['triangle_size'\][^\n]+\nconfig\.n_jobs = setting\.get\("config\.n_jobs", 1\)[^\n]+\nconfig\.nx = 2 \*\* glevel[^\n]+\nconfig\.x_width = triangle_size[^\n]+\nconfig\.dx = config\.x_width / config\.nx""",
    ]

    if is_plot_file:
        new_imports = """from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()"""
    else:
        new_imports = """from utils.config import AnalysisConfig

config = AnalysisConfig()"""

    replaced = False
    for pattern in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, new_imports, content)
            replaced = True
            break

    # If not replaced, try a more general approach - remove the whole setting block manually
    if not replaced and "with open('setting.json'" in content:
        # Find and remove lines from "# ファイルを開いて" or "with open" to "config.dx =
        # config.x_width / config.nx"
        lines = content.split("\n")
        new_lines = []
        skip = False
        imports_added = False

        for i, line in enumerate(lines):
            if "# ファイルを開いてJSONを読み込む" in line or (
                skip == False and "with open('setting.json'" in line
            ):
                skip = True
                if not imports_added:
                    if i > 0:
                        new_lines.append("")  # Keep spacing
                    new_lines.append(new_imports)
                    imports_added = True
                continue

            if skip:
                # Check if we've reached the end of the setting block
                if (
                    line.strip() == ""
                    or line.startswith("time_list")
                    or line.startswith("r_max")
                    or line.startswith("output_folder")
                    or line.startswith("folder")
                    or line.startswith("def ")
                    or line.startswith("nr =")
                    or line.startswith("R =")
                    or line.startswith("f =")
                    or line.startswith("pres_s =")
                    or line.startswith("Rd =")
                    or line.startswith("Cp =")
                    or line.startswith("L =")
                    or line.startswith("vgrid =")
                    or line.startswith("xgrid =")
                    or line.startswith("X, Y =")
                ):
                    skip = False
                    new_lines.append(line)
                continue

            new_lines.append(line)

        content = "\n".join(new_lines)
        replaced = True

    # Remove json import if not needed
    if "json.load" not in content and "json.dump" not in content:
        content = re.sub(r"^import json\n", "", content, flags=re.MULTILINE)

    # Clean up multiple empty lines
    content = re.sub(r"\n\n\n+", "\n\n", content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    """Main function."""
    azim_mean_dir = Path("azim_mean")

    # Find files still with setting.json
    py_files = []
    for py_file in azim_mean_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            if "with open('setting.json'" in f.read():
                py_files.append(py_file)

    print(f"Found {len(py_files)} files still loading setting.json")
    fixed_count = 0

    for py_file in py_files:
        if fix_incomplete_setting_block(py_file):
            print(f"  Fixed: {py_file}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
