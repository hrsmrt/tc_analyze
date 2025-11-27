#!/usr/bin/env python3
"""
Add dtype=np.float32 to np.zeros() and np.empty() calls for memory optimization.
"""

import os
import re


def optimize_dtype(filepath):
    """Add dtype=np.float32 to numpy array allocations."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Pattern 1: np.zeros(...) without dtype → np.zeros(..., dtype=np.float32)
    # But skip if dtype is already specified
    def add_dtype(match):
        full = match.group(0)
        # Skip if dtype is already specified
        if 'dtype' in full:
            return full
        # Skip if it's clearly an integer array (minlength, for bincount)
        if 'minlength' in full:
            return full
        # Add dtype=np.float32 before the closing parenthesis
        return full[:-1] + ', dtype=np.float32)'

    # Match np.zeros(...) or np.empty(...) - capture the full call
    # This pattern matches: np.zeros(any_content) where any_content doesn't contain 'dtype'
    patterns = [
        r'np\.zeros\([^)]+\)(?!\s*,\s*dtype)',
        r'np\.empty\([^)]+\)(?!\s*,\s*dtype)',
    ]

    for pattern in patterns:
        # Find all matches
        matches = list(re.finditer(pattern, content))
        # Process in reverse to maintain positions
        for match in reversed(matches):
            full = match.group(0)
            # Double-check: skip if dtype already there or if it's minlength
            if 'dtype' not in full and 'minlength' not in full:
                # Add dtype=np.float32
                new_text = full[:-1] + ', dtype=np.float32)'
                content = content[:match.start()] + new_text + content[match.end():]

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Main function."""
    # Target files identified earlier
    target_files = [
        "analysis/azimuthal/q8/calc/azim_q8_wind_relative_calc.py",
        "analysis/azimuthal/q8/calc/azim_q8_3d_calc.py",
        "analysis/azimuthal/basic/calc/azim_stream_calc.py",
        "analysis/azimuthal/basic/calc/azim_wind10m_calc.py",
        "analysis/azimuthal/basic/calc/azim_stream2_calc.py",
        "analysis/azimuthal/basic/calc/azim_pert_3d_calc.py",
        "analysis/azimuthal/basic/calc/azim_3d_calc.py",
        "analysis/azimuthal/eliassen/calc/azim_N2_calc.py",
        "analysis/vertical/profile/calc/vortex_region_calc.py",
        "analysis/vertical/q4/calc/vorticity_z_calc.py",
    ]

    modified = []
    for file in target_files:
        if optimize_dtype(file):
            modified.append(file)
            print(f"✓ {file}")

    print(f"\n最適化完了: {len(modified)}ファイル")


if __name__ == '__main__':
    main()
