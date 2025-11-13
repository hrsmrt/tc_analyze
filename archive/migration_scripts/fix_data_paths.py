#!/usr/bin/env python3
"""
Fix data paths in plot files that incorrectly use config.input_folder
"""
import re
from pathlib import Path

# Mapping of file patterns to correct data paths
PATH_MAPPINGS = {
    "azim_momentum_plot.py": "./data/azim/momentum/",
    "azim_stream_max_plot.py": "./data/azim/stream/",
    "azim_stream2_plot.py": "./data/azim/stream2/",
    "azim_theta_e_plot.py": "./data/azim/theta_e/",
    "azim_theta_plot.py": "./data/azim/theta/",
    "azim_vorticity_z_absolute_plot.py": "./data/azim/vorticity_z_absolute/",
    "azim_vorticity_z_plot.py": "./data/azim/vorticity_z/",
    "azim_B_plot.py": "./data/azim/eliassen/B/",
    "azim_buoyancy_plot.py": "./data/azim/eliassen/buoyancy/",
    "azim_gamma_plot.py": "./data/azim/eliassen/gamma/",
    "azim_I_prime2_plot.py": "./data/azim/eliassen/I_prime2/",
    "azim_I2_plot.py": "./data/azim/eliassen/I2/",
    "azim_N2_plot.py": "./data/azim/eliassen/N2/",
    "azim_R_plot.py": "./data/azim/eliassen/R/",
    "azim_xi_plot.py": "./data/azim/eliassen/xi/",
}


def fix_file(filepath):
    """Fix data path in a single file"""
    filename = filepath.name

    # Check if this file needs fixing
    correct_path = None
    for pattern, path in PATH_MAPPINGS.items():
        if pattern in filename:
            correct_path = path
            break

    if not correct_path:
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Replace incorrect path
    content = re.sub(
        r'f"\{config\.input_folder\}t\{str\(t\)\.zfill\(3\)\}\.npy"',
        f'f"{correct_path}t{{str(t).zfill(3)}}.npy"',
        content,
    )

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    azim_mean_dir = Path("/Users/hiroshimurata/tc_analyze/azim_mean")

    fixed_count = 0
    for pattern in PATH_MAPPINGS.keys():
        files = list(azim_mean_dir.rglob(pattern))
        for filepath in files:
            if fix_file(filepath):
                print(f"✓ Fixed {filepath}")
                fixed_count += 1

    print(f"\n{'=' * 60}")
    print(f"Fixed {fixed_count} files")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
