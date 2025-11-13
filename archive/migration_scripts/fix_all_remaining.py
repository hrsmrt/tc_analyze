#!/usr/bin/env python3
"""
Fix all remaining files with old setting.json pattern.
"""

import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix files with old setting.json loading pattern."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Check if it still has the old pattern
    if (
        "with open('setting.json'" not in content
        and 'with open("setting.json"' not in content
    ):
        return False

    # Check if config is already imported
    if "from utils.config import AnalysisConfig" in content:
        return False

    is_plot_file = "_plot" in filepath.name or "plot" in filepath.name

    # Add sys.path modification if not present
    if "sys.path.append" not in content:
        # Find where to insert (after imports)
        import_section_end = 0
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_section_end = i

        # Insert sys.path.append after the last import
        if import_section_end > 0:
            sys_path_lines = [
                "",
                "script_dir = os.path.dirname(os.path.abspath(__file__))",
                'sys.path.append(os.path.join(script_dir, ".."))',
                "",
            ]
            lines = (
                lines[: import_section_end + 1]
                + sys_path_lines
                + lines[import_section_end + 1:]
            )
            content = "\n".join(lines)

    # Determine what imports to add
    if is_plot_file:
        new_imports = """from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()"""
    else:
        new_imports = """from utils.config import AnalysisConfig

config = AnalysisConfig()"""

    # Pattern to match the entire old setting block (flexible version)
    # This handles both single quotes and comments before
    patterns = [
        # With comment
        r'# ファイルを開いてJSONを読み込む\s*\n\s*with open\([\'"]setting\.json[\'"][^\)]*\)[^:]*:[^{]*\{[^}]*\}[^\n]*\n(?:[^\n]*(?:glevel|nt|dt|triangle_size|nx|ny|nz|x_width|y_width|dx|dy|input_folder)[^\n]*\n)+',
        # Without comment
        r'with open\([\'"]setting\.json[\'"][^\)]*\)[^:]*:[^{]*\{[^}]*\}[^=]*=(?:[^\n]*\n)+?(?=\n(?:folder|output_folder|time_list|r_max|z_max|def |nr =|R =|f =|center_[xy]_list|vgrid|xgrid|X, Y =|\n))',
    ]

    replaced = False
    for pattern in patterns:
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, new_imports + "\n\n", content, flags=re.MULTILINE)
            replaced = True
            break

    # If not replaced with regex, try line-by-line approach
    if not replaced and (
        "with open('setting.json'" in content or 'with open("setting.json"' in content
    ):
        lines = content.split("\n")
        new_lines = []
        skip = False
        imports_added = False
        in_setting_block = False

        for i, line in enumerate(lines):
            # Detect start of setting block
            if not in_setting_block and (
                "# ファイルを開いてJSONを読み込む" in line
                or (
                    not skip
                    and (
                        "with open('setting.json'" in line
                        or 'with open("setting.json"' in line
                    )
                )
            ):
                in_setting_block = True
                skip = True
                if not imports_added:
                    new_lines.append("")
                    new_lines.append(new_imports)
                    new_lines.append("")
                    imports_added = True
                continue

            if skip:
                # Check if we've reached the end of the setting block
                # End patterns: empty line followed by non-setting code, or specific
                # variable assignments
                stripped = line.strip()
                if (
                    (
                        stripped == ""
                        and i + 1 < len(lines)
                        and lines[i + 1].strip()
                        and not any(
                            var in lines[i + 1]
                            for var in [
                                "glevel",
                                "nt",
                                "dt",
                                "triangle_size",
                                "nx",
                                "ny",
                                "nz",
                                "x_width",
                                "y_width",
                                "dx",
                                "dy",
                                "input_folder",
                                "setting",
                            ]
                        )
                    )
                    or stripped.startswith("folder =")
                    or stripped.startswith("output_folder =")
                    or stripped.startswith("time_list =")
                    or stripped.startswith("r_max =")
                    or stripped.startswith("z_max =")
                    or stripped.startswith("def ")
                    or stripped.startswith("nr =")
                    or stripped.startswith("R =")
                    or stripped.startswith("f =")
                    or "center_x_list" in stripped
                    or "center_y_list" in stripped
                    or stripped.startswith("vgrid =")
                    or stripped.startswith("xgrid =")
                    or "X, Y =" in stripped
                    or "X,Y =" in stripped
                    or stripped.startswith("x =")
                    or stripped.startswith("y =")
                    or (stripped.startswith("pres_s =") and "setting" not in stripped)
                    or (stripped.startswith("Rd =") and "setting" not in stripped)
                    or (stripped.startswith("Cp =") and "setting" not in stripped)
                    or (stripped.startswith("L =") and "setting" not in stripped)
                ):
                    skip = False
                    in_setting_block = False
                    new_lines.append(line)
                continue

            new_lines.append(line)

        content = "\n".join(new_lines)
        replaced = True

    # Replace variable references
    replacements = {
        "nt": "config.nt",
        "dt_hour": "config.dt_hour",
        "nx": "config.nx",
        "ny": "config.ny",
        "nz": "config.nz",
        "dx": "config.dx",
        "dy": "config.dy",
        "x_width": "config.x_width",
        "y_width": "config.y_width",
        "input_folder": "config.input_folder",
    }

    # Be careful to only replace standalone variable names, not parts of other identifiers
    for old_var, new_var in replacements.items():
        # Use word boundaries to avoid replacing parts of other variables
        content = re.sub(rf"\b{old_var}\b", new_var, content)

    # Remove json import if not needed anymore
    if (
        "json.load" not in content
        and "json.dump" not in content
        and "json.loads" not in content
    ):
        content = re.sub(r"^import json\s*\n", "", content, flags=re.MULTILINE)
        content = re.sub(r"^import json\s*#[^\n]*\n", "", content, flags=re.MULTILINE)

    # Replace style argument parsing for plot files
    if is_plot_file and "sys.argv" in content and "mpl_style_sheet" in content:
        # Replace the manual sys.argv parsing
        old_style_pattern = r"# コマンドライン引数が3つ以上あるかを確認\s*\n\s*if len\(sys\.argv\) > [12]:[^\n]*\n[^\n]*mpl_style_sheet[^\n]*\n[^\n]*print[^\n]*\n\s*else:[^\n]*\n[^\n]*print[^\n]*\n"
        if re.search(old_style_pattern, content):
            content = re.sub(
                old_style_pattern, "mpl_style_sheet = parse_style_argument()\n", content
            )
        else:
            # Try simpler pattern
            old_style_pattern2 = r"if len\(sys\.argv\) > [12]:[^\n]*\n[^\n]*mpl_style_sheet[^\n]*\n[^\n]*print[^\n]*\nelse:[^\n]*\n[^\n]*print[^\n]*\n"
            content = re.sub(
                old_style_pattern2,
                "mpl_style_sheet = parse_style_argument()\n",
                content,
            )

    # Clean up multiple empty lines
    content = re.sub(r"\n\n\n+", "\n\n", content)

    # Write back if changed
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    """Main function."""
    # Target directories
    target_patterns = [
        "3d/*.py",
        "2d/*.py",
        "center/*.py",
        "z_profile/*.py",
        "z_profile_q4/*.py",
        "symmetrisity/*.py",
        "azim_mean/*.py",
        "azim_mean/**/*.py",
    ]

    from pathlib import Path

    py_files = []
    for pattern in target_patterns:
        py_files.extend(Path(".").glob(pattern))

    # Filter to only files still using setting.json
    files_to_fix = []
    for py_file in py_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                if (
                    "with open('setting.json'" in content
                    or 'with open("setting.json"' in content
                ):
                    if "from utils.config import AnalysisConfig" not in content:
                        files_to_fix.append(py_file)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")

    print(f"Found {len(files_to_fix)} files to fix")

    fixed_count = 0
    failed_files = []

    for py_file in files_to_fix:
        try:
            if fix_file(py_file):
                print(f"  ✓ Fixed: {py_file}")
                fixed_count += 1
            else:
                print(f"  - Skipped: {py_file}")
        except Exception as e:
            print(f"  ✗ Failed: {py_file} - {e}")
            failed_files.append(py_file)

    print(f"\n{'=' * 60}")
    print(f"Fixed {fixed_count} files")
    if failed_files:
        print(f"Failed {len(failed_files)} files:")
        for f in failed_files:
            print(f"  - {f}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
