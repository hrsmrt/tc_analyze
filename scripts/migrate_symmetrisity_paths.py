#!/usr/bin/env python3
"""Migrate symmetrisity analysis scripts to new directory structure."""

import os
import re
from pathlib import Path

# Define path mapping rules
PATH_MAPPINGS = [
    # Output paths: symmetrisity → diagnostics/symmetrisity
    (r'config\.get_data_path\("symmetrisity",\s*"([^"]+)"\)', r'config.get_tc_centric_path("diagnostics", "symmetrisity/\1")'),
    (r"config\.get_data_path\('symmetrisity',\s*'([^']+)'\)", r"config.get_tc_centric_path('diagnostics', 'symmetrisity/\1')"),
    (r'config\.get_data_path\("symmetrisity",\s*varname\)', r'config.get_tc_centric_path("diagnostics", f"symmetrisity/{varname}")'),
    (r"config\.get_data_path\('symmetrisity',\s*varname\)", r"config.get_tc_centric_path('diagnostics', f'symmetrisity/{varname}')"),

    # Load paths: azim → azimuthal/basic
    (r'config\.get_data_path\("azim",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "basic/\1")'),
    (r"config\.get_data_path\('azim',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'basic/\1')"),
    (r'config\.get_data_path\("azim",\s*varname\)', r'config.get_tc_centric_path("azimuthal", f"basic/{varname}")'),
    (r"config\.get_data_path\('azim',\s*varname\)", r"config.get_tc_centric_path('azimuthal', f'basic/{varname}')"),

    # Load paths: 3d → vortex_region/3d (for relative_wind data)
    (r'config\.get_data_path\("3d",\s*"relative_wind_([^"]+)"\)', r'config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_\1")'),
    (r"config\.get_data_path\('3d',\s*'relative_wind_([^']+)'\)", r"config.get_tc_centric_path('vortex_region', '3d/ms_wind_relative_\1')"),
]


def migrate_file(filepath):
    """Migrate a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply all mappings
    for pattern, replacement in PATH_MAPPINGS:
        content = re.sub(pattern, replacement, content)

    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Migrate all symmetrisity calc files."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis/diagnostics/symmetrisity/calc")

    calc_files = list(base_dir.glob("*_calc.py"))

    print(f"Found {len(calc_files)} calc files in diagnostics/symmetrisity/")
    print()

    migrated = 0
    for filepath in sorted(calc_files):
        if migrate_file(filepath):
            print(f"✓ Migrated: {filepath.name}")
            migrated += 1
        else:
            print(f"  Skipped: {filepath.name} (no changes)")

    print()
    print(f"Migrated {migrated}/{len(calc_files)} files")


if __name__ == "__main__":
    main()
