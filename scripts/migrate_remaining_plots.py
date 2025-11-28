#!/usr/bin/env python3
"""Migrate remaining plot files with additional patterns."""

import os
import re
from pathlib import Path

# Additional path mapping rules
ADDITIONAL_MAPPINGS = {
    'whole_domain': [
        # get_fig_path with 3 args: (category, subcategory, varname)
        (r'config\.get_fig_path\("2d",\s*"whole_domain",\s*([^\)]+)\)',
         r'config.get_domain_path("whole_domain", f"2d/{\\1}", data_type="fig")'),
        (r"config\.get_fig_path\('2d',\s*'whole_domain',\s*([^\)]+)\)",
         r"config.get_domain_path('whole_domain', f'2d/{\\1}', data_type='fig')"),

        (r'config\.get_fig_path\("3d",\s*"whole_domain",\s*([^\)]+)\)',
         r'config.get_domain_path("whole_domain", f"3d/{\\1}", data_type="fig")'),
        (r"config\.get_fig_path\('3d',\s*'whole_domain',\s*([^\)]+)\)",
         r"config.get_domain_path('whole_domain', f'3d/{\\1}', data_type='fig')"),

        # get_data_path with no args or single arg
        (r'config\.get_data_path\(\)',
         r'config.get_domain_path("whole_domain", "2d")'),
        (r'config\.get_data_path\("([^"]+)"\)',
         r'config.get_domain_path("whole_domain", "2d/\1")'),
    ],

    'azimuthal': [
        # get_fig_path("azim", varname) with variable
        (r'config\.get_fig_path\("azim",\s*varname\)',
         r'config.get_tc_centric_path("azimuthal", f"basic/{varname}", data_type="fig")'),
        (r"config\.get_fig_path\('azim',\s*varname\)",
         r"config.get_tc_centric_path('azimuthal', f'basic/{varname}', data_type='fig')"),

        # get_data_path("azim", varname) with variable
        (r'config\.get_data_path\("azim",\s*varname\)',
         r'config.get_tc_centric_path("azimuthal", f"basic/{varname}")'),
        (r"config\.get_data_path\('azim',\s*varname\)",
         r"config.get_tc_centric_path('azimuthal', f'basic/{varname}')"),

        # get_fig_path("azim", VARNAME) with constant
        (r'config\.get_fig_path\("azim",\s*VARNAME\)',
         r'config.get_tc_centric_path("azimuthal", f"basic/{VARNAME}", data_type="fig")'),
        (r"config\.get_fig_path\('azim',\s*VARNAME\)",
         r"config.get_tc_centric_path('azimuthal', f'basic/{VARNAME}', data_type='fig')"),
    ],

    'vortex_region': [
        # get_data_path with 2 args for vortex_region
        (r'config\.get_data_path\("2d",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vortex_region", "2d/\1")'),
        (r"config\.get_data_path\('2d',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vortex_region', '2d/\1')"),

        (r'config\.get_data_path\("3d",\s*"relative_wind_([^"]+)"\)',
         r'config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_\1")'),
        (r"config\.get_data_path\('3d',\s*'relative_wind_([^']+)'\)",
         r"config.get_tc_centric_path('vortex_region', '3d/ms_wind_relative_\1')"),

        (r'config\.get_data_path\("3d",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vortex_region", "3d/\1")'),
        (r"config\.get_data_path\('3d',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vortex_region', '3d/\1')"),
    ],

    'vertical': [
        # get_data_path for z_profile
        (r'config\.get_data_path\("z_profile",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vertical", "profile_vortex/\1")'),
        (r"config\.get_data_path\('z_profile',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vertical', 'profile_vortex/\1')"),
        (r'config\.get_data_path\("z_profile"\)',
         r'config.get_domain_path("vertical", "profile")'),
        (r"config\.get_data_path\('z_profile'\)",
         r"config.get_domain_path('vertical', 'profile')"),
    ],

    'center': [
        # get_fig_path("center") - single arg for center trajectory plots
        (r'config\.get_fig_path\("center"\)',
         r'config.get_center_path("ss_slp", data_type="fig")'),
        (r"config\.get_fig_path\('center'\)",
         r"config.get_center_path('ss_slp', data_type='fig')"),
    ],
}


def migrate_file(filepath, category_mappings):
    """Migrate a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # Apply all mappings for this category
    for pattern, replacement in category_mappings:
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
    """Migrate remaining plot files."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis")

    total_migrated = 0
    total_files = 0

    for directory, mappings in ADDITIONAL_MAPPINGS.items():
        dir_path = base_dir / directory
        if not dir_path.exists():
            continue

        # Find all Python files (not just *_plot.py)
        py_files = list(dir_path.glob("**/*.py"))
        # Filter out files with new methods already
        files_to_check = []
        for f in py_files:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                if 'get_data_path' in content or 'get_fig_path' in content:
                    if not ('get_domain_path' in content or 'get_center_path' in content or 'get_tc_centric_path' in content):
                        files_to_check.append(f)

        if not files_to_check:
            continue

        print(f"\n{directory}/:")
        print(f"  Found {len(files_to_check)} files needing migration")

        migrated = 0
        for filepath in sorted(files_to_check):
            if migrate_file(filepath, mappings):
                print(f"  ✓ {filepath.relative_to(dir_path)}")
                migrated += 1
                total_migrated += 1
            total_files += 1

        print(f"  Migrated: {migrated}/{len(files_to_check)}")

    print(f"\n{'='*80}")
    print(f"TOTAL: Migrated {total_migrated}/{total_files} files")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
