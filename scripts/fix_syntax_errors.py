#!/usr/bin/env python3
"""Fix syntax errors from migration."""

import re
from pathlib import Path

# Files with VARNAME variable - replace {\1} with {VARNAME}
FILES_WITH_VARNAME = [
    "analysis/whole_domain/2d/plot/whole_domain.py",
    "analysis/whole_domain/3d/plot/whole_domain.py",
    "analysis/whole_domain/3d/plot/divergence_whole_domain_plot.py",
    "analysis/whole_domain/3d/plot/streamplot_whole_domain.py",
    "analysis/whole_domain/3d/plot/vorticity_z_absolute_whole_domain_plot.py",
    "analysis/whole_domain/3d/plot/whole_domain_wind_uv_abs_plot.py",
]

# Files with fixed names - replace {\1} with actual directory name
FILES_WITH_FIXED_NAME = {
    "analysis/whole_domain/2d/plot/slp_tppn.py": "slp_tppn",
    "analysis/whole_domain/2d/plot/ss_wind10m_abs_whole_domain.py": "ss_wind10m_abs_whole_domain",
}

# Files with extra parenthesis
FILES_WITH_EXTRA_PAREN = [
    "analysis/whole_domain/3d/plot/whole_domain_two_levels.py",
    "analysis/whole_domain/3d/plot/whole_domain_two_levels_filled.py",
]


def fix_file(filepath, fix_type, replacement=None):
    """Fix a single file."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze")
    full_path = base_dir / filepath

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    if fix_type == "varname":
        # Replace {\1} with {VARNAME}
        content = content.replace(r'{\1}', '{VARNAME}')

    elif fix_type == "fixed":
        # Replace f"2d/{\1}" or f"3d/{\1}" with the actual name
        if "2d" in str(filepath):
            content = content.replace(r'f"2d/{\1}"', f'"2d/{replacement}"')
        elif "3d" in str(filepath):
            content = content.replace(r'f"3d/{\1}"', f'"3d/{replacement}"')

    elif fix_type == "paren":
        # Remove extra closing parenthesis - pattern: , data_type="fig"))
        content = re.sub(
            r', data_type="fig"\)\)',
            r', data_type="fig")',
            content
        )

    if content != original_content:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Fix all syntax errors."""
    print("Fixing syntax errors from migration...\n")

    fixed_count = 0

    # Fix VARNAME files
    print("=== Files with VARNAME variable ===")
    for filepath in FILES_WITH_VARNAME:
        if fix_file(filepath, "varname"):
            print(f"✓ {filepath}")
            fixed_count += 1
        else:
            print(f"  {filepath} (no changes)")

    # Fix fixed-name files
    print("\n=== Files with fixed names ===")
    for filepath, dirname in FILES_WITH_FIXED_NAME.items():
        if fix_file(filepath, "fixed", dirname):
            print(f"✓ {filepath}")
            fixed_count += 1
        else:
            print(f"  {filepath} (no changes)")

    # Fix extra parenthesis files
    print("\n=== Files with extra parenthesis ===")
    for filepath in FILES_WITH_EXTRA_PAREN:
        if fix_file(filepath, "paren"):
            print(f"✓ {filepath}")
            fixed_count += 1
        else:
            print(f"  {filepath} (no changes)")

    print(f"\n{'='*80}")
    print(f"Fixed {fixed_count} files")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
