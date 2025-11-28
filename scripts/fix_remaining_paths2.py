#!/usr/bin/env python3
"""Fix remaining old path method calls - batch 2."""

import re
from pathlib import Path

# Additional path mapping rules
MAPPINGS = [
    # azimuthal/basic - with varname variable
    (r"config\.get_data_path\(['\"]azim['\"],\s*varname\)",
     r'config.get_tc_centric_path("azimuthal", f"basic/{varname}")'),

    # azimuthal/basic - wind_radial with "b" suffix
    (r'config\.get_fig_path\(["\']azim["\']\s*,\s*["\']wind_radial["\']\s*,\s*["\']b["\']\)',
     r'config.get_tc_centric_path("azimuthal", "basic/wind_radial_b", data_type="fig")'),

    # azimuthal/eliassen/buoyancy
    (r"config\.get_data_path\(['\"]azim['\"],\s*['\"]eliassen['\"],\s*['\"]buoyancy['\"]\)",
     r'config.get_tc_centric_path("azimuthal", "eliassen/buoyancy")'),

    # diagnostics/symmetrisity - with varname
    (r'config\.get_fig_path\(["\']symmetrisity["\']\s*,\s*varname\)',
     r'config.get_tc_centric_path("diagnostics", f"symmetrisity/{varname}", data_type="fig")'),

    # diagnostics/symmetrisity - specific variables
    (r"config\.get_data_path\(['\"]symmetrisity['\"],\s*['\"]relative_wind_radial['\"]\)",
     r'config.get_tc_centric_path("diagnostics", "symmetrisity/relative_wind_radial")'),
    (r"config\.get_data_path\(['\"]symmetrisity['\"],\s*['\"]relative_wind_tangential['\"]\)",
     r'config.get_tc_centric_path("diagnostics", "symmetrisity/relative_wind_tangential")'),

    # diagnostics/sums
    (r"config\.get_data_path\(['\"]sums['\"]\)",
     r'config.get_tc_centric_path("diagnostics", "sums")'),

    # vertical/profile - vortex_region with varname
    (r'config\.get_fig_path\(["\']z_profile["\']\s*,\s*["\']vortex_region["\']\s*,\s*varname\)',
     r'config.get_tc_centric_path("vertical", f"profile_vortex/{varname}", data_type="fig")'),

    # vertical/profile - whole_domain with varname
    (r'config\.get_fig_path\(["\']z_profile["\']\s*,\s*["\']whole_domain["\']\s*,\s*varname\)',
     r'config.get_domain_path("vertical", f"profile/{varname}", data_type="fig")'),

    # vertical/q4
    (r"config\.get_data_path\(['\"]z_profile_q4['\"],\s*['\"]zeta['\"]\)",
     r'config.get_tc_centric_path("vertical", "q4/zeta")'),

    # whole_domain/2d - whole_domain_with_low2
    (r'config\.get_fig_path\(["\']2d["\']\s*,\s*["\']whole_domain_with_low2["\']\s*,\s*VARNAME\)',
     r'config.get_domain_path("whole_domain", f"2d/whole_domain_with_low2/{VARNAME}", data_type="fig")'),

    # whole_domain/2d - ss_slp_min (center folder)
    (r'config\.get_fig_path\(["\']center["\']\)',
     r'config.get_domain_path("whole_domain", "2d/ss_slp_min", data_type="fig")'),
]


def fix_file(filepath):
    """Fix a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    for pattern, replacement in MAPPINGS:
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
