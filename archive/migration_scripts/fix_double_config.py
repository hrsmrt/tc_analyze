#!/usr/bin/env python3
"""
Fix double config references caused by the refactoring script.
"""

import re
from pathlib import Path

def fix_double_config(filepath: Path) -> bool:
    """Fix double config.config. references."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix triple or more nested config references
    content = re.sub(r'config\.config\.config\.', 'config.', content)
    content = re.sub(r'config\.config\.', 'config.', content)

    # Fix Parallel n_jobs parameter
    content = re.sub(r'Parallel\(config\.n_jobs=config\.n_jobs\)', 'Parallel(n_jobs=config.n_jobs)', content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function."""
    azim_mean_dir = Path("azim_mean")
    py_files = sorted(azim_mean_dir.rglob("*.py"))

    print(f"Checking {len(py_files)} files for double config references...")
    fixed_count = 0

    for py_file in py_files:
        if fix_double_config(py_file):
            print(f"  Fixed: {py_file}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
