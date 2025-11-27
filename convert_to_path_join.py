#!/usr/bin/env python3
"""
Convert f-string path patterns to os.path.join() format.
"""

import os
import re
import sys


def has_fstring_expressions(s):
    """Check if a string contains f-string expressions (curly braces)."""
    return '{' in s and '}' in s


def convert_fstring_path(match):
    """
    Convert f-string path pattern to os.path.join().

    Handles patterns like:
    - f"{folder}/file.txt" → os.path.join(folder, "file.txt")
    - f"{folder}/t{expr}.npy" → os.path.join(folder, f"t{expr}.npy")
    - f"{config.get_data_path('a', 'b')}/file.npy" → os.path.join(config.get_data_path('a', 'b'), "file.npy")
    """
    full_match = match.group(0)
    prefix = match.group(1)  # The part before /
    suffix = match.group(2)  # The part after /

    # Remove the f" and " around the whole expression
    # Extract the variable/expression part
    var_part = prefix.strip('{}')

    # Check if suffix contains f-string expressions
    if has_fstring_expressions(suffix):
        # Keep as f-string
        return f'os.path.join({var_part}, f"{suffix}")'
    else:
        # Convert to regular string
        return f'os.path.join({var_part}, "{suffix}")'


def add_os_import(content):
    """Add 'import os' if not already present."""
    if re.search(r'^import os$', content, re.MULTILINE):
        return content

    # Find the first import statement
    import_match = re.search(r'^import ', content, re.MULTILINE)
    if import_match:
        # Add before the first import
        pos = import_match.start()
        return content[:pos] + 'import os\n' + content[pos:]
    else:
        # Add at the beginning
        return 'import os\n' + content


def convert_file(filepath):
    """Convert a single Python file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pattern 1: f"{variable}/..." or f"{function(...)}/..."
    # Matches: f"{folder}/file.txt", f"{config.get_data_path('a')}/file.npy", etc.
    # Captures: (variable/expression part, filename part)
    pattern1 = r'f"(\{[^}]+\})/([^"]+)"'

    # Apply conversion
    content = re.sub(pattern1, convert_fstring_path, content)

    # If content changed, add os import
    if content != original_content:
        content = add_os_import(content)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    return False


def main():
    """Main function."""
    analysis_dir = "/Users/hiroshimurata/tc_analyze/analysis"

    modified_files = []

    # Walk through all .py files
    for root, dirs, files in os.walk(analysis_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if convert_file(filepath):
                    modified_files.append(filepath)
                    print(f"✓ {filepath}")

    print(f"\n変換完了: {len(modified_files)} ファイル")

    return 0


if __name__ == '__main__':
    sys.exit(main())
