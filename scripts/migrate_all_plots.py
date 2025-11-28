#!/usr/bin/env python3
"""Migrate all plot files to new directory structure."""

import os
import re
from pathlib import Path

# Define path mapping rules for different categories
PATH_MAPPINGS = {
    'vortex_region': [
        # 2d vortex_region
        (r'config\.get_fig_path\("2d",\s*"vortex_region",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vortex_region", "2d/\1", data_type="fig")'),
        (r"config\.get_fig_path\('2d',\s*'vortex_region',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vortex_region', '2d/\1', data_type='fig')"),

        # 3d vortex_region - relative_wind needs special handling
        (r'config\.get_fig_path\("3d",\s*"vortex_region",\s*"relative_wind_([^"]+)"\)',
         r'config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_\1", data_type="fig")'),
        (r"config\.get_fig_path\('3d',\s*'vortex_region',\s*'relative_wind_([^']+)'\)",
         r"config.get_tc_centric_path('vortex_region', '3d/ms_wind_relative_\1', data_type='fig')"),

        # 3d vortex_region - general
        (r'config\.get_fig_path\("3d",\s*"vortex_region",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vortex_region", "3d/\1", data_type="fig")'),
        (r"config\.get_fig_path\('3d',\s*'vortex_region',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vortex_region', '3d/\1', data_type='fig')"),
    ],

    'whole_domain': [
        # 2d whole_domain
        (r'config\.get_fig_path\("2d",\s*"([^"]+)"\)',
         r'config.get_domain_path("whole_domain", "2d/\1", data_type="fig")'),
        (r"config\.get_fig_path\('2d',\s*'([^']+)'\)",
         r"config.get_domain_path('whole_domain', '2d/\1', data_type='fig')"),

        # 3d whole_domain
        (r'config\.get_fig_path\("3d",\s*"([^"]+)"\)',
         r'config.get_domain_path("whole_domain", "3d/\1", data_type="fig")'),
        (r"config\.get_fig_path\('3d',\s*'([^']+)'\)",
         r"config.get_domain_path('whole_domain', '3d/\1', data_type='fig')"),
    ],

    'azimuthal_basic': [
        # azim → azimuthal/basic/
        (r'config\.get_fig_path\("azim",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("azimuthal", "basic/\1", data_type="fig")'),
        (r"config\.get_fig_path\('azim',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('azimuthal', 'basic/\1', data_type='fig')"),

        # azim_pert → azimuthal/basic/pert/
        (r'config\.get_fig_path\("azim_pert",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("azimuthal", "basic/pert/\1", data_type="fig")'),
        (r"config\.get_fig_path\('azim_pert',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('azimuthal', 'basic/pert/\1', data_type='fig')"),
    ],

    'azimuthal_eliassen': [
        # azim, eliassen → azimuthal/eliassen/
        (r'config\.get_fig_path\("azim",\s*"eliassen",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("azimuthal", "eliassen/\1", data_type="fig")'),
        (r"config\.get_fig_path\('azim',\s*'eliassen',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('azimuthal', 'eliassen/\1', data_type='fig')"),
    ],

    'azimuthal_momentum': [
        # azim, eq_momentum_u → azimuthal/momentum/u/
        (r'config\.get_fig_path\("azim",\s*"eq_momentum_u",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("azimuthal", "momentum/u/\1", data_type="fig")'),
        (r"config\.get_fig_path\('azim',\s*'eq_momentum_u',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('azimuthal', 'momentum/u/\1', data_type='fig')"),

        # azim, eq_momentum_w → azimuthal/momentum/w/
        (r'config\.get_fig_path\("azim",\s*"eq_momentum_w",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("azimuthal", "momentum/w/\1", data_type="fig")'),
        (r"config\.get_fig_path\('azim',\s*'eq_momentum_w',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('azimuthal', 'momentum/w/\1', data_type='fig')"),
    ],

    'azimuthal_q8': [
        # azim_q8 → azimuthal/q8/
        (r'config\.get_fig_path\("azim_q8",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("azimuthal", "q8/\1", data_type="fig")'),
        (r"config\.get_fig_path\('azim_q8',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('azimuthal', 'q8/\1', data_type='fig')"),
    ],

    'vertical': [
        # z_profile → vertical/profile
        (r'config\.get_fig_path\("z_profile",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vertical", "profile_vortex/\1", data_type="fig")'),
        (r"config\.get_fig_path\('z_profile',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vertical', 'profile_vortex/\1', data_type='fig')"),
        (r'config\.get_fig_path\("z_profile"\)',
         r'config.get_domain_path("vertical", "profile", data_type="fig")'),
        (r"config\.get_fig_path\('z_profile'\)",
         r"config.get_domain_path('vertical', 'profile', data_type='fig')"),

        # z_profile_q4 → vertical/q4
        (r'config\.get_fig_path\("z_profile_q4",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("vertical", "q4/\1", data_type="fig")'),
        (r"config\.get_fig_path\('z_profile_q4',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('vertical', 'q4/\1', data_type='fig')"),
    ],

    'diagnostics': [
        # sums → diagnostics/sums
        (r'config\.get_fig_path\("sums",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("diagnostics", "sums/\1", data_type="fig")'),
        (r"config\.get_fig_path\('sums',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('diagnostics', 'sums/\1', data_type='fig')"),
        (r'config\.get_fig_path\("sums"\)',
         r'config.get_tc_centric_path("diagnostics", "sums", data_type="fig")'),
        (r"config\.get_fig_path\('sums'\)",
         r"config.get_tc_centric_path('diagnostics', 'sums', data_type='fig')"),

        # symmetrisity → diagnostics/symmetrisity
        (r'config\.get_fig_path\("symmetrisity",\s*"([^"]+)"\)',
         r'config.get_tc_centric_path("diagnostics", "symmetrisity/\1", data_type="fig")'),
        (r"config\.get_fig_path\('symmetrisity',\s*'([^']+)'\)",
         r"config.get_tc_centric_path('diagnostics', 'symmetrisity/\1', data_type='fig')"),
    ],

    'center': [
        # center paths
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
    """Migrate all plot files."""
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis")

    # Map directories to their mapping rules
    dir_to_mappings = {
        'vortex_region': PATH_MAPPINGS['vortex_region'],
        'whole_domain': PATH_MAPPINGS['whole_domain'],
        'vertical': PATH_MAPPINGS['vertical'],
        'diagnostics': PATH_MAPPINGS['diagnostics'],
        'center': PATH_MAPPINGS['center'],
    }

    # Azimuthal needs all its mappings
    azimuthal_mappings = (
        PATH_MAPPINGS['azimuthal_basic'] +
        PATH_MAPPINGS['azimuthal_eliassen'] +
        PATH_MAPPINGS['azimuthal_momentum'] +
        PATH_MAPPINGS['azimuthal_q8']
    )
    dir_to_mappings['azimuthal'] = azimuthal_mappings

    total_migrated = 0
    total_files = 0

    for directory, mappings in dir_to_mappings.items():
        dir_path = base_dir / directory
        if not dir_path.exists():
            continue

        plot_files = list(dir_path.glob("**/*_plot.py")) + list(dir_path.glob("**/plot/*.py"))

        if not plot_files:
            continue

        print(f"\n{directory}/:")
        print(f"  Found {len(plot_files)} plot files")

        migrated = 0
        for filepath in sorted(plot_files):
            if migrate_file(filepath, mappings):
                print(f"  ✓ {filepath.relative_to(dir_path)}")
                migrated += 1
                total_migrated += 1
            total_files += 1

        print(f"  Migrated: {migrated}/{len(plot_files)}")

    print(f"\n{'='*80}")
    print(f"TOTAL: Migrated {total_migrated}/{total_files} files")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
