#!/usr/bin/env python3
"""Final batch migration for remaining files."""

import os
import re
from pathlib import Path

# Final path mapping rules
FINAL_MAPPINGS = [
    # config.get_data_path() with no args - assume whole_domain/2d
    (r'config\.get_data_path\(\)',
     r'config.get_domain_path("whole_domain", "2d")'),

    # azim2, azim_pert2, azim_core variants → azimuthal/basic/
    (r'config\.get_fig_path\("azim2",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"basic2/{varname}", data_type="fig")'),
    (r'config\.get_data_path\("azim2",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"basic2/{varname}")'),
    (r"config\.get_data_path\('azim2',\s*varname\)",
     r"config.get_tc_centric_path('azimuthal', f'basic2/{varname}')"),

    (r'config\.get_fig_path\("azim_pert2",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"basic/pert2/{varname}", data_type="fig")'),
    (r'config\.get_data_path\("azim_pert2",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"basic/pert2/{varname}")'),
    (r"config\.get_data_path\('azim_pert2',\s*varname\)",
     r"config.get_tc_centric_path('azimuthal', f'basic/pert2/{varname}')"),

    (r'config\.get_fig_path\("azim_pert",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"basic/pert/{varname}", data_type="fig")'),
    (r'config\.get_data_path\("azim_pert",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"basic/pert/{varname}")'),
    (r"config\.get_data_path\('azim_pert',\s*varname\)",
     r"config.get_tc_centric_path('azimuthal', f'basic/pert/{varname}')"),

    (r'config\.get_fig_path\("azim_core",\s*"([^"]+)"\)',
     r'config.get_tc_centric_path("azimuthal", "basic/core/\1", data_type="fig")'),

    # azim_q8 variants
    (r'config\.get_fig_path\("azim_q8",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"q8/{varname}", data_type="fig")'),
    (r'config\.get_data_path\("azim_q8",\s*varname\)',
     r'config.get_tc_centric_path("azimuthal", f"q8/{varname}")'),
    (r"config\.get_data_path\('azim_q8',\s*varname\)",
     r"config.get_tc_centric_path('azimuthal', f'q8/{varname}')"),

    # azim with specific names like wind_radial2
    (r'config\.get_data_path\("azim",\s*"wind_radial2"\)',
     r'config.get_tc_centric_path("azimuthal", "basic/wind_radial2")'),
    (r"config\.get_data_path\('azim',\s*'wind_radial2'\)",
     r"config.get_tc_centric_path('azimuthal', 'basic/wind_radial2')"),

    (r'config\.get_data_path\("azim",\s*"wind_tangential2"\)',
     r'config.get_tc_centric_path("azimuthal", "basic/wind_tangential2")'),
    (r"config\.get_data_path\('azim',\s*'wind_tangential2'\)",
     r"config.get_tc_centric_path('azimuthal', 'basic/wind_tangential2')"),

    (r'config\.get_fig_path\("azim",\s*"wind_tangential",\s*"b"\)',
     r'config.get_tc_centric_path("azimuthal", "basic/wind_tangential_b", data_type="fig")'),

    # symmetrisity variants
    (r'config\.get_data_path\("symmetrisity",\s*varname\)',
     r'config.get_tc_centric_path("diagnostics", f"symmetrisity/{varname}")'),
    (r"config\.get_data_path\('symmetrisity',\s*varname\)",
     r"config.get_tc_centric_path('diagnostics', f'symmetrisity/{varname}')"),

    # vortex_region variants
    (r'config\.get_fig_path\("3d",\s*"vortex_region_r250",\s*VARNAME\)',
     r'config.get_tc_centric_path("vortex_region", f"3d_r250/{VARNAME}", data_type="fig")'),
    (r'config\.get_fig_path\("3d",\s*"vortex_region",\s*VARNAME\)',
     r'config.get_tc_centric_path("vortex_region", f"3d/{VARNAME}", data_type="fig")'),
    (r'config\.get_fig_path\("2d",\s*"vortex_region",\s*VARNAME\)',
     r'config.get_tc_centric_path("vortex_region", f"2d/{VARNAME}", data_type="fig")'),
    (r'config\.get_fig_path\("2d",\s*"vortex_region2",\s*"([^"]+)"\)',
     r'config.get_tc_centric_path("vortex_region", "2d_v2/\1", data_type="fig")'),

    (r'config\.get_fig_path\("3d",\s*"theta_e",\s*"vortex_region"\)',
     r'config.get_tc_centric_path("vortex_region", "3d/theta_e", data_type="fig")'),

    # whole_domain variants with single arg
    (r'config\.get_fig_path\("cape"\)',
     r'config.get_domain_path("whole_domain", "3d/cape", data_type="fig")'),
    (r'config\.get_fig_path\("psi"\)',
     r'config.get_domain_path("whole_domain", "3d/psi", data_type="fig")'),

    # whole_domain with 3 args
    (r'config\.get_fig_path\("2d",\s*"y_ave",\s*VARNAME\)',
     r'config.get_domain_path("whole_domain", f"2d/y_ave/{VARNAME}", data_type="fig")'),
    (r'config\.get_fig_path\("3d",\s*"([^"]+)",\s*VARNAME\)',
     r'config.get_domain_path("whole_domain", f"3d/\1/{VARNAME}", data_type="fig")'),
]


def migrate_file(filepath):
    """Migrate a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # Apply all mappings
    for pattern, replacement in FINAL_MAPPINGS:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True

    # Write back if changed
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Migrate final batch of files."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis")

    # Find files needing migration
    files_to_check = []
    for py_file in base_dir.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue

        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        has_old = 'get_data_path' in content or 'get_fig_path' in content
        has_new = 'get_domain_path' in content or 'get_center_path' in content or 'get_tc_centric_path' in content

        if has_old and not has_new:
            files_to_check.append(py_file)

    print(f"Found {len(files_to_check)} files needing migration\n")

    migrated = 0
    for filepath in sorted(files_to_check):
        if migrate_file(filepath):
            print(f"✓ {filepath.relative_to(base_dir.parent)}")
            migrated += 1

    print(f"\n{'='*80}")
    print(f"Migrated {migrated}/{len(files_to_check)} files")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
