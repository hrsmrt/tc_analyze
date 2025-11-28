#!/usr/bin/env python3
"""Fix all remaining old path method calls."""

import re
from pathlib import Path

# Path mapping rules for data loading
DATA_LOAD_MAPPINGS = [
    # vortex_region
    (r"config\.get_data_path\(['\"]3d['\"],\s*['\"]vorticity_z['\"]\)",
     r'config.get_domain_path("whole_domain", "3d/vorticity_z")'),
    (r"config\.get_data_path\(['\"]3d['\"],\s*['\"]divergence['\"]\)",
     r'config.get_domain_path("whole_domain", "3d/divergence")'),
    (r"config\.get_data_path\(['\"]2d['\"],\s*['\"]wind10m_radial['\"]\)",
     r'config.get_tc_centric_path("vortex_region", "2d/ss_wind10m_radial")'),
    (r"config\.get_data_path\(['\"]2d['\"],\s*['\"]wind10m_tangential['\"]\)",
     r'config.get_tc_centric_path("vortex_region", "2d/ss_wind10m_tangential")'),

    # azimuthal/momentum/u
    (r"config\.get_data_path\(['\"]azim['\"],\s*['\"]eq_momentum_u['\"],\s*['\"]([^'\"]+)['\"]\)",
     r'config.get_tc_centric_path("azimuthal", "momentum/u/\1")'),
    (r"config\.get_data_path\(['\"]azim['\"],\s*['\"]eq_momentum_u['\"]\)",
     r'config.get_tc_centric_path("azimuthal", "momentum/u")'),

    # azimuthal/momentum/w
    (r"config\.get_data_path\(['\"]azim['\"],\s*['\"]eq_momentum_w['\"]\)",
     r'config.get_tc_centric_path("azimuthal", "momentum/w")'),

    # azimuthal/q8
    (r"config\.get_data_path\(['\"]azim_q8['\"],\s*['\"]([^'\"]+)['\"]\)",
     r'config.get_tc_centric_path("azimuthal", "q8/\1")'),

    # azimuthal/basic
    (r"config\.get_data_path\(['\"]azim['\"],\s*['\"]([^'\"]+)['\"]\)",
     r'config.get_tc_centric_path("azimuthal", "basic/\1")'),

    # relative wind (3d)
    (r"config\.get_data_path\(['\"]3d['\"],\s*['\"]relative_u['\"]\)",
     r'config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_radial")'),
    (r"config\.get_data_path\(['\"]3d['\"],\s*['\"]relative_v['\"]\)",
     r'config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_tangential")'),
]

# Path mapping rules for output folders
OUTPUT_MAPPINGS = [
    # vortex_region psi plots
    (r'config\.get_fig_path\(["\']3d["\']\s*,\s*["\']psi["\']\s*,\s*["\']vortex_region["\']\)',
     r'config.get_tc_centric_path("vortex_region", "3d/psi", data_type="fig")'),
    (r'config\.get_fig_path\(["\']3d["\']\s*,\s*["\']psi["\']\s*,\s*["\']r200["\']\)',
     r'config.get_tc_centric_path("vortex_region", "3d/psi_r200", data_type="fig")'),
]


def fix_file(filepath):
    """Fix a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # Apply data load mappings
    for pattern, replacement in DATA_LOAD_MAPPINGS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True

    # Apply output mappings
    for pattern, replacement in OUTPUT_MAPPINGS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Fix all remaining files."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis")

    # Find all Python files
    py_files = list(base_dir.glob("**/*.py"))

    print(f"Scanning {len(py_files)} Python files...\n")

    fixed_count = 0
    for filepath in sorted(py_files):
        if fix_file(filepath):
            print(f"✓ {filepath.relative_to(base_dir.parent)}")
            fixed_count += 1

    print(f"\n{'='*80}")
    print(f"Fixed {fixed_count} files")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
