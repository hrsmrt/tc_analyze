#!/usr/bin/env python3
"""
Manual dtype optimization with specific patterns for each file.
"""

import re


def optimize_file(filepath, patterns):
    """Apply specific pattern replacements to a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    for old, new in patterns:
        content = content.replace(old, new)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


# Define specific patterns for each file
FILE_PATTERNS = {
    "analysis/azimuthal/basic/calc/azim_3d_calc.py": [
        ("np.zeros((config.nz, len(count_r)))",
         "np.zeros((config.nz, len(count_r)), dtype=np.float32)"),
    ],
    "analysis/azimuthal/basic/calc/azim_pert_3d_calc.py": [
        ("np.zeros((config.nz, len(count_r)))",
         "np.zeros((config.nz, len(count_r)), dtype=np.float32)"),
    ],
    "analysis/azimuthal/basic/calc/azim_wind10m_calc.py": [
        ("azim_sum_radial = np.zeros(max_bin)",
         "azim_sum_radial = np.zeros(max_bin, dtype=np.float32)"),
        ("azim_sum_tangential = np.zeros(max_bin)",
         "azim_sum_tangential = np.zeros(max_bin, dtype=np.float32)"),
    ],
    "analysis/azimuthal/q8/calc/azim_q8_3d_calc.py": [
        ("azim_sum = np.zeros((config.nz, max_bin, 8))",
         "azim_sum = np.zeros((config.nz, max_bin, 8), dtype=np.float32)"),
    ],
    "analysis/azimuthal/q8/calc/azim_q8_wind_relative_calc.py": [
        ("dtype=np.float64", "dtype=np.float32"),
    ],
    "analysis/azimuthal/basic/calc/azim_stream_calc.py": [
        ("phi = np.zeros_like(rho)",
         "phi = np.zeros_like(rho, dtype=np.float32)"),
    ],
    "analysis/azimuthal/basic/calc/azim_stream2_calc.py": [
        ("phi = np.zeros_like(rho)",
         "phi = np.zeros_like(rho, dtype=np.float32)"),
    ],
    "analysis/azimuthal/eliassen/calc/azim_N2_calc.py": [
        ("db_dz = np.zeros((config.nz - 1, nr))",
         "db_dz = np.zeros((config.nz - 1, nr), dtype=np.float32)"),
    ],
    "analysis/vertical/profile/calc/vortex_region_calc.py": [
        ("z_profile_data = np.zeros(config.nz)",
         "z_profile_data = np.zeros(config.nz, dtype=np.float32)"),
    ],
    "analysis/vertical/q4/calc/vorticity_z_calc.py": [
        ("z_profile_q = np.zeros((config.nt, config.nz, 4))",
         "z_profile_q = np.zeros((config.nt, config.nz, 4), dtype=np.float32)"),
    ],
}


def main():
    """Main function."""
    modified = []

    for filepath, patterns in FILE_PATTERNS.items():
        if optimize_file(filepath, patterns):
            modified.append(filepath)
            print(f"✓ {filepath}")
        else:
            print(f"⚠ {filepath} - no changes")

    print(f"\n最適化完了: {len(modified)}ファイル")


if __name__ == '__main__':
    main()
