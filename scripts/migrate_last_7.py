#!/usr/bin/env python3
"""Migrate last 7 files manually."""

import re
from pathlib import Path

FILES_AND_PATTERNS = [
    (
        "analysis/whole_domain/3d/plot/psi_plot.py",
        [
            (r'config\.get_fig_path\("3d",\s*"psi",\s*"whole_region"\)',
             r'config.get_domain_path("whole_domain", "3d/psi", data_type="fig")'),
            (r"config\.get_data_path\('3d',\s*'vorticity_z'\)",
             r"config.get_domain_path('whole_domain', '3d/vorticity_z')"),
        ]
    ),
    (
        "analysis/whole_domain/3d/plot/theta_e_plot_whole_region.py",
        [
            (r'config\.get_fig_path\("3d",\s*"theta_e",\s*"whole_region"\)',
             r'config.get_domain_path("whole_domain", "3d/theta_e", data_type="fig")'),
        ]
    ),
    (
        "analysis/whole_domain/3d/plot/whole_domain_slp_with_ms_pres_level.py",
        [
            # Match multiline pattern - need to be careful with whitespace
            (r'config\.get_fig_path\(\s*"3d",\s*"whole_domain_slp_with_ms_pres_level",\s*f"z\{Z_MS_PRES\}_smooth\{SIGMA:.1f\}"\s*\)',
             r'config.get_domain_path("whole_domain", f"3d/whole_domain_slp_with_ms_pres_level/z{Z_MS_PRES}_smooth{SIGMA:.1f}", data_type="fig")'),
            (r'config\.get_fig_path\(\s*"3d",\s*"whole_domain_slp_with_ms_pres_level",\s*f"z\{Z_MS_PRES\}"\s*\)',
             r'config.get_domain_path("whole_domain", f"3d/whole_domain_slp_with_ms_pres_level/z{Z_MS_PRES}", data_type="fig")'),
        ]
    ),
    (
        "analysis/whole_domain/3d/plot/whole_domain_pressure_two_levels_with_centers.py",
        [
            (r'config\.get_fig_path\(\s*"3d",\s*"whole_domain_pressure_two_levels_with_centers",\s*f"z\{Z1\}_z\{Z2\}_centers_\{z_center_str\}_smooth\{SIGMA:.1f\}"\s*\)',
             r'config.get_domain_path("whole_domain", f"3d/whole_domain_pressure_two_levels_with_centers/z{Z1}_z{Z2}_centers_{z_center_str}_smooth{SIGMA:.1f}", data_type="fig")'),
            (r'config\.get_fig_path\(\s*"3d",\s*"whole_domain_pressure_two_levels_with_centers",\s*f"z\{Z1\}_z\{Z2\}_centers_\{z_center_str\}"\s*\)',
             r'config.get_domain_path("whole_domain", f"3d/whole_domain_pressure_two_levels_with_centers/z{Z1}_z{Z2}_centers_{z_center_str}", data_type="fig")'),
        ]
    ),
    (
        "analysis/whole_domain/3d/plot/whole_domain_two_levels.py",
        [
            (r'config\.get_fig_path\("3d",\s*"whole_domain_two_levels",\s*os\.path\.join\(VARNAME,\s*f"_z\{Z1\}_z\{Z2\}_smooth\{SIGMA:.1f\}"\)',
             r'config.get_domain_path("whole_domain", os.path.join(f"3d/whole_domain_two_levels/{VARNAME}", f"_z{Z1}_z{Z2}_smooth{SIGMA:.1f}"), data_type="fig")'),
            (r'config\.get_fig_path\("3d",\s*"whole_domain_two_levels",\s*os\.path\.join\(VARNAME,\s*f"_z\{Z1\}_z\{Z2\}"\)',
             r'config.get_domain_path("whole_domain", os.path.join(f"3d/whole_domain_two_levels/{VARNAME}", f"_z{Z1}_z{Z2}"), data_type="fig")'),
        ]
    ),
    (
        "analysis/whole_domain/3d/plot/whole_domain_two_levels_filled.py",
        [
            (r'config\.get_fig_path\("3d",\s*"whole_domain_two_levels_filled",\s*os\.path\.join\(VARNAME,\s*f"_z\{Z1\}_z\{Z2\}_smooth\{SIGMA:.1f\}"\)',
             r'config.get_domain_path("whole_domain", os.path.join(f"3d/whole_domain_two_levels_filled/{VARNAME}", f"_z{Z1}_z{Z2}_smooth{SIGMA:.1f}"), data_type="fig")'),
            (r'config\.get_fig_path\("3d",\s*"whole_domain_two_levels_filled",\s*os\.path\.join\(VARNAME,\s*f"_z\{Z1\}_z\{Z2\}"\)',
             r'config.get_domain_path("whole_domain", os.path.join(f"3d/whole_domain_two_levels_filled/{VARNAME}", f"_z{Z1}_z{Z2}"), data_type="fig")'),
        ]
    ),
]


def migrate_file(filepath, patterns):
    """Migrate a single file with specified patterns."""
    filepath = Path(filepath)
    base_dir = Path("/Users/hiroshimurata/tc_analyze")
    full_path = base_dir / filepath

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Migrate last 7 files."""
    print("Migrating last 7 files...\n")

    migrated = 0
    for filepath, patterns in FILES_AND_PATTERNS:
        if migrate_file(filepath, patterns):
            print(f"✓ {filepath}")
            migrated += 1
        else:
            print(f"  {filepath} (no changes)")

    print(f"\n{'='*80}")
    print(f"Migrated {migrated}/{len(FILES_AND_PATTERNS)} files")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
