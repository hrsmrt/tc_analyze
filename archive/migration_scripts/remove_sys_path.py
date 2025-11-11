#!/usr/bin/env python3
"""
Remove sys.path.append lines from all Python files after package installation.
"""

import re
from pathlib import Path

def remove_sys_path(filepath: Path) -> bool:
    """Remove sys.path.append and related lines from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # パターン1: 通常の sys.path.append
    pattern1 = r'^script_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n^sys\.path\.append\(os\.path\.join\(script_dir, "\.\."\)\)\n'
    content = re.sub(pattern1, '', content, flags=re.MULTILINE)

    # パターン2: normpath を使った sys.path.append
    pattern2 = r'^script_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n^sys\.path\.append\(os\.path\.normpath\(os\.path\.join\(script_dir, "\.\.", "module"\)\)\)\n'
    content = re.sub(pattern2, '', content, flags=re.MULTILINE)

    # パターン3: target_path を使った sys.path.append (z_profile などで使用)
    pattern3 = r'^script_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n^target_path = os\.path\.join\(script_dir, [^\n]+\n^sys\.path\.append\(target_path\)\n'
    content = re.sub(pattern3, '', content, flags=re.MULTILINE)

    # 空行が連続している場合は1つにまとめる
    content = re.sub(r'\n\n\n+', '\n\n', content)

    # import sys が他で使われていない場合は削除
    if 'sys.' not in content or content.count('sys.') == content.count('sys.path'):
        if 'import sys\n' in content and 'sys.argv' not in content and 'sys.exit' not in content:
            content = re.sub(r'^import sys\n', '', content, flags=re.MULTILINE)

    # import os が他で使われていない場合は削除（ただし os.path や os.makedirs などは残す）
    # os は様々な箇所で使われるので、削除は慎重に
    # 今回は削除しない方が安全

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function."""
    target_dirs = [
        "3d", "2d", "center", "z_profile",
        "z_profile_q4", "symmetrisity", "azim_mean"
    ]

    fixed_files = []

    for dir_name in target_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'sys.path.append' in content:
                        if remove_sys_path(py_file):
                            fixed_files.append(py_file)
                            print(f"  ✓ {py_file}")
            except Exception as e:
                print(f"  ✗ Error processing {py_file}: {e}")

    print(f"\n{'='*60}")
    print(f"Removed sys.path.append from {len(fixed_files)} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
