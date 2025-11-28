#!/usr/bin/env python3
"""Migrate azimuthal analysis scripts to new directory structure."""

import os
import re
from pathlib import Path

# Define path mapping rules
PATH_MAPPINGS = [
    # azimuthal/basic: azim → basic/
    (r'config\.get_data_path\("azim",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "basic/\1")'),
    (r"config\.get_data_path\('azim',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'basic/\1')"),

    # azimuthal/basic: azim_pert → basic/pert/
    (r'config\.get_data_path\("azim_pert",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "basic/pert/\1")'),
    (r"config\.get_data_path\('azim_pert',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'basic/pert/\1')"),

    # azimuthal/eliassen: azim, eliassen → eliassen/
    (r'config\.get_data_path\("azim",\s*"eliassen",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "eliassen/\1")'),
    (r"config\.get_data_path\('azim',\s*'eliassen',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'eliassen/\1')"),

    # azimuthal/eliassen: Load paths azim, eliassen without third arg
    (r'config\.get_data_path\("azim",\s*"eliassen"\)', r'config.get_tc_centric_path("azimuthal", "eliassen")'),
    (r"config\.get_data_path\('azim',\s*'eliassen'\)", r"config.get_tc_centric_path('azimuthal', 'eliassen')"),

    # azimuthal/momentum/u: azim, eq_momentum_u → momentum/u/
    (r'config\.get_data_path\("azim",\s*"eq_momentum_u",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "momentum/u/\1")'),
    (r"config\.get_data_path\('azim',\s*'eq_momentum_u',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'momentum/u/\1')"),

    # azimuthal/momentum/w: azim, eq_momentum_w → momentum/w/
    (r'config\.get_data_path\("azim",\s*"eq_momentum_w",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "momentum/w/\1")'),
    (r"config\.get_data_path\('azim',\s*'eq_momentum_w',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'momentum/w/\1')"),

    # azimuthal/q8: azim_q8 → q8/
    (r'config\.get_data_path\("azim_q8",\s*"([^"]+)"\)', r'config.get_tc_centric_path("azimuthal", "q8/\1")'),
    (r"config\.get_data_path\('azim_q8',\s*'([^']+)'\)", r"config.get_tc_centric_path('azimuthal', 'q8/\1')"),
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
    """Migrate all azimuthal calc files."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis/azimuthal")

    calc_files = list(base_dir.glob("**/*_calc.py"))

    print(f"Found {len(calc_files)} calc files in azimuthal/")
    print()

    migrated = 0
    for filepath in sorted(calc_files):
        if migrate_file(filepath):
            print(f"✓ Migrated: {filepath.relative_to(base_dir.parent)}")
            migrated += 1
        else:
            print(f"  Skipped: {filepath.relative_to(base_dir.parent)} (no changes)")

    print()
    print(f"Migrated {migrated}/{len(calc_files)} files")


if __name__ == "__main__":
    main()
