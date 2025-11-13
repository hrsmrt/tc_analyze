#!/usr/bin/env python3
"""
Batch refactoring script for azim_mean directory files.
This script updates all Python files to use the new utils.config and utils.grid modules.
"""

import re
from pathlib import Path

# Old pattern to remove (14 lines)
OLD_SETTING_BLOCK = r"""# ファイルを開いてJSONを読み込む
with open\('setting\.json', 'r', encoding='utf-8'\) as f:
    setting = json\.load\(f\)
glevel = setting\['glevel'\]
nt = setting\['nt'\]
dt = setting\['dt_output'\]
dt_hour = int\(dt / 3600\)
triangle_size = setting\['triangle_size'\]
nx = 2 \*\* glevel
ny = 2 \*\* glevel
nz = 74
x_width = triangle_size
y_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting\['input_folder'\]
n_jobs = setting\.get\("n_jobs", 1\)"""

# Alternate old pattern (some files may vary slightly)
OLD_SETTING_BLOCK_ALT = r"""with open\('setting\.json', 'r', encoding='utf-8'\) as f:
    setting = json\.load\(f\)

glevel = setting\['glevel'\]
nt = setting\['nt'\]
dt = setting\['dt_output'\]
dt_hour = int\(dt / 3600\)
triangle_size = setting\['triangle_size'\]
nx = 2 \*\* glevel
ny = 2 \*\* glevel
nz = 74
x_width = triangle_size
y_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting\['input_folder'\]
n_jobs = setting\.get\("n_jobs", 1\)"""

# New config imports
NEW_CONFIG_IMPORTS = """from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)"""

# Variables to replace mapping
VAR_REPLACEMENTS = {
    r"\bnx\b": "config.nx",
    r"\bny\b": "config.ny",
    r"\bnz\b": "config.nz",
    r"\bnt\b": "config.nt",
    r"\bdt_hour\b": "config.dt_hour",
    r"\bdx\b": "config.dx",
    r"\bdy\b": "config.dy",
    r"\bx_width\b": "config.x_width",
    r"\by_width\b": "config.y_width",
    r"\binput_folder\b": "config.input_folder",
    r"\bn_jobs\b": "config.n_jobs",
}

# Import cleanup patterns
IMPORT_CLEANUP = [
    (r"^import json\n", ""),  # Remove json import unless used elsewhere
    (r"^script_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n", ""),
    (
        r'^sys\.path\.append\(os\.path\.normpath\(os\.path\.join\(script_dir, "..", "module"\)\)\)\n',
        "",
    ),
    (r"^# 実行ファイル（この\.pyファイル）を基準に相対パスを指定\n", ""),
]

# Old style parsing pattern
OLD_STYLE_PATTERN = r"""if len\(sys\.argv\) > \d+:
    mpl_style_sheet = sys\.argv\[\d+\]
    print\(f"Using style: \{mpl_style_sheet\}"\)
else:
    print\("No style sheet specified, using default\."\)"""


def refactor_calc_file(filepath):
    """Refactor a calculation file (non-plot)."""
    print(f"Processing calc file: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Check if already refactored
    if "from utils.config import AnalysisConfig" in content:
        print(f"  Already refactored, skipping...")
        return False

    # Remove old setting block
    content = re.sub(OLD_SETTING_BLOCK, NEW_CONFIG_IMPORTS, content, flags=re.MULTILINE)
    if content == original_content:
        content = re.sub(
            OLD_SETTING_BLOCK_ALT, NEW_CONFIG_IMPORTS, content, flags=re.MULTILINE
        )

    # Clean up imports
    for pattern, replacement in IMPORT_CLEANUP:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Remove 'import json' if not actually using JSON elsewhere
    if (
        "json.load" not in content
        and "json.dump" not in content
        and "import json" in content
    ):
        content = content.replace("import json\n", "")

    # Replace variable references (after imports but within code)
    for old_var, new_var in VAR_REPLACEMENTS.items():
        content = re.sub(old_var, new_var, content)

    # Special case: replace grid coordinate creation
    content = re.sub(
        r"""# 格子点座標（m単位）\nx = \(np\.arange\(config\.nx\) \+ 0\.5\) \* config\.dx\ny = \(np\.arange\(config\.ny\) \+ 0\.5\) \* config\.dy\nX, Y = np\.meshgrid\(x, y\)""",
        "X, Y = grid.X, grid.Y",
        content,
        flags=re.MULTILINE,
    )

    # Handle vgrid_filepath if present
    content = re.sub(r"setting\['vgrid_filepath'\]", "config.vgrid_filepath", content)

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ Refactored")
        return True
    else:
        print(f"  No changes made")
        return False


def refactor_plot_file(filepath):
    """Refactor a plot file."""
    print(f"Processing plot file: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Check if already refactored
    if "from utils.config import AnalysisConfig" in content:
        print(f"  Already refactored, skipping...")
        return False

    # First add plotting import if style argument is used
    if "sys.argv" in content and "mpl_style_sheet" in content:
        # Add utils.plotting import
        config_imports = """from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()"""

        # Remove old setting block
        content = re.sub(OLD_SETTING_BLOCK, config_imports, content, flags=re.MULTILINE)
        if content == original_content:
            content = re.sub(
                OLD_SETTING_BLOCK_ALT, config_imports, content, flags=re.MULTILINE
            )

        # Replace style argument parsing
        # Find which argument index is used
        style_match = re.search(r"sys\.argv\[(\d+)\]", content)
        if style_match:
            arg_index = style_match.group(1)
            old_style_block = f"""if len(sys.argv) > {arg_index}:
    mpl_style_sheet = sys.argv[{arg_index}]
    print(f"Using style: {{mpl_style_sheet}}")
else:
    print("No style sheet specified, using default.")"""

            new_style_block = f"""mpl_style_sheet = parse_style_argument(arg_index={arg_index})
if mpl_style_sheet:
    plt.style.use(mpl_style_sheet)"""

            content = content.replace(old_style_block, new_style_block)
    else:
        # No style argument, just config
        content = re.sub(
            OLD_SETTING_BLOCK, NEW_CONFIG_IMPORTS, content, flags=re.MULTILINE
        )
        if content == original_content:
            content = re.sub(
                OLD_SETTING_BLOCK_ALT, NEW_CONFIG_IMPORTS, content, flags=re.MULTILINE
            )

    # Clean up imports
    for pattern, replacement in IMPORT_CLEANUP:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Remove 'import json' if not actually using JSON elsewhere
    if (
        "json.load" not in content
        and "json.dump" not in content
        and "import json" in content
    ):
        content = content.replace("import json\n", "")

    # Replace variable references
    for old_var, new_var in VAR_REPLACEMENTS.items():
        content = re.sub(old_var, new_var, content)

    # Special case: replace time_list
    content = re.sub(
        r"time_list = \[t \* config\.dt_hour for t in range\(config\.nt\)\]",
        "time_list = config.time_list",
        content,
    )

    # Handle vgrid_filepath if present
    content = re.sub(r"setting\['vgrid_filepath'\]", "config.vgrid_filepath", content)
    content = re.sub(
        r'f"\{setting\[\'vgrid_filepath\'\]\}"', "config.vgrid_filepath", content
    )

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ Refactored")
        return True
    else:
        print(f"  No changes made")
        return False


def main():
    """Main refactoring function."""
    azim_mean_dir = Path("azim_mean")

    if not azim_mean_dir.exists():
        print(f"Error: {azim_mean_dir} directory not found")
        return

    # Get all Python files recursively
    py_files = list(azim_mean_dir.rglob("*.py"))

    print(f"Found {len(py_files)} Python files in {azim_mean_dir}/")
    print()

    calc_count = 0
    plot_count = 0
    skipped_count = 0

    for py_file in sorted(py_files):
        # Determine if calc or plot file
        if "_plot" in py_file.name or py_file.name.startswith("plot_"):
            if refactor_plot_file(py_file):
                plot_count += 1
            else:
                skipped_count += 1
        else:
            if refactor_calc_file(py_file):
                calc_count += 1
            else:
                skipped_count += 1

    print()
    print("=" * 60)
    print(f"Refactoring complete!")
    print(f"  Calc files refactored: {calc_count}")
    print(f"  Plot files refactored: {plot_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"  Total: {len(py_files)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
