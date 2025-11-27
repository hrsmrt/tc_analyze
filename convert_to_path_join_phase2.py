#!/usr/bin/env python3
"""
Phase 2: Handle edge cases and remaining patterns.
- f"{var}filename" without slash (where var might end with /)
- Trailing slashes in path variables
"""

import os
import re


def fix_trailing_slash_patterns(content):
    """
    Fix patterns like:
    folder_z = os.path.join(folder, f"z{str(z).zfill(2)}/")
    →
    folder_z = os.path.join(folder, f"z{str(z).zfill(2)}")

    And then convert:
    f"{folder_z}t{...}.png"
    →
    os.path.join(folder_z, f"t{...}.png")
    """
    # First, remove trailing slashes from os.path.join results
    # Pattern: os.path.join(..., ".../" or f".../"
    content = re.sub(
        r'os\.path\.join\(([^)]+), (f?"[^"]+)/"\)',
        r'os.path.join(\1, \2")',
        content
    )

    # Now convert f"{var}filename" patterns where var doesn't contain function calls
    # This handles cases like f"{folder_z}t001.png"
    # Pattern: f"{simple_var}rest" where simple_var is [a-zA-Z_][a-zA-Z0-9_]*
    def replace_simple_var(match):
        var = match.group(1)
        rest = match.group(2)

        # Check if rest contains f-string expressions
        if '{' in rest and '}' in rest:
            return f'os.path.join({var}, f"{rest}")'
        else:
            return f'os.path.join({var}, "{rest}")'

    # Match f"{var}..." where var is a simple identifier (not containing dots or brackets)
    content = re.sub(
        r'f"\{([a-zA-Z_][a-zA-Z0-9_]*)\}([^"]+)"',
        replace_simple_var,
        content
    )

    return content


def process_file(filepath):
    """Process a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    content = fix_trailing_slash_patterns(content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Main function."""
    analysis_dir = "/Users/hiroshimurata/tc_analyze/analysis"
    modified = []

    for root, dirs, files in os.walk(analysis_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                if process_file(path):
                    modified.append(path)
                    print(f"✓ {path}")

    print(f"\n変換完了: {len(modified)} ファイル")


if __name__ == '__main__':
    main()
