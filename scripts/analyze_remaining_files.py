#!/usr/bin/env python3
"""Analyze remaining files that need migration."""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_file(filepath):
    """Analyze a file for old path patterns."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for old path methods (excluding new ones)
    old_patterns = [
        r'config\.get_data_path\(',
        r'config\.get_fig_path\(',
    ]

    new_patterns = [
        r'config\.get_domain_path\(',
        r'config\.get_center_path\(',
        r'config\.get_tc_centric_path\(',
    ]

    has_old = any(re.search(pattern, content) for pattern in old_patterns)
    has_new = any(re.search(pattern, content) for pattern in new_patterns)

    if has_old and not has_new:
        return 'needs_migration'
    elif has_new:
        return 'migrated'
    else:
        return 'no_path_calls'


def main():
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis")

    categories = defaultdict(lambda: {'needs_migration': [], 'migrated': [], 'no_path_calls': []})

    for py_file in base_dir.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue

        # Determine category
        parts = py_file.relative_to(base_dir).parts
        if len(parts) >= 1:
            category = parts[0]
        else:
            category = "unknown"

        status = analyze_file(py_file)
        categories[category][status].append(py_file.relative_to(base_dir))

    # Print results
    print("=" * 80)
    print("REMAINING FILES ANALYSIS")
    print("=" * 80)
    print()

    total_needs_migration = 0
    total_migrated = 0

    for category in sorted(categories.keys()):
        needs = len(categories[category]['needs_migration'])
        migrated = len(categories[category]['migrated'])
        no_calls = len(categories[category]['no_path_calls'])

        total_needs_migration += needs
        total_migrated += migrated

        print(f"{category}:")
        print(f"  ✓ Migrated: {migrated}")
        print(f"  ⚠ Needs migration: {needs}")
        print(f"  − No path calls: {no_calls}")

        if needs > 0:
            print(f"  Files needing migration:")
            for f in sorted(categories[category]['needs_migration'])[:10]:
                print(f"    - {f}")
            if needs > 10:
                print(f"    ... and {needs - 10} more")
        print()

    print("=" * 80)
    print(f"TOTAL: {total_migrated} migrated, {total_needs_migration} need migration")
    print("=" * 80)


if __name__ == "__main__":
    main()
