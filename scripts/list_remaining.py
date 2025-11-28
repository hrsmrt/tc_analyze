#!/usr/bin/env python3
"""List all remaining files and their patterns."""

import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_file(filepath):
    """Extract path patterns from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    patterns = []

    # Find all get_data_path and get_fig_path calls
    for match in re.finditer(r'config\.(get_data_path|get_fig_path)\([^)]*\)', content):
        patterns.append(match.group(0))

    return patterns


def main():
    base_dir = Path("/Users/hiroshimurata/tc_analyze/analysis")

    remaining_files = {}

    for py_file in base_dir.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue

        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        has_old = 'get_data_path' in content or 'get_fig_path' in content
        has_new = 'get_domain_path' in content or 'get_center_path' in content or 'get_tc_centric_path' in content

        if has_old and not has_new:
            patterns = analyze_file(py_file)
            if patterns:
                remaining_files[py_file] = patterns

    print(f"Found {len(remaining_files)} files needing migration\n")

    # Group by pattern
    pattern_groups = defaultdict(list)
    for filepath, patterns in remaining_files.items():
        for pattern in patterns:
            pattern_groups[pattern].append(filepath)

    print("=" * 80)
    print("PATTERNS FOUND:")
    print("=" * 80)

    for pattern in sorted(pattern_groups.keys(), key=lambda x: len(pattern_groups[x]), reverse=True):
        files = pattern_groups[pattern]
        print(f"\n{pattern} ({len(files)} files)")
        for f in sorted(files)[:5]:
            print(f"  - {f.relative_to(base_dir.parent)}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")


if __name__ == "__main__":
    main()
