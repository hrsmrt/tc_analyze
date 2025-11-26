#!/usr/bin/env python
"""
dtype最適化スクリプト

np.zeros, np.empty, np.onesにdtype=np.float32を追加して
メモリ使用量を約50%削減します。
"""

import re
import sys
from pathlib import Path


def optimize_file(filepath):
    """ファイルのdtypeを最適化"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # パターン1: np.zeros((config.nz, max_bin)) → np.zeros((config.nz, max_bin), dtype=np.float32)
    # 誤った変換も修正: )), dtype → ), dtype
    content = re.sub(r'\)\),\s*dtype=np\.float32', r'), dtype=np.float32', content)

    pattern1 = r'np\.zeros\(\(config\.nz,\s*max_bin\)\)(?!,\s*dtype)'
    if re.search(pattern1, content):
        content = re.sub(pattern1, r'np.zeros((config.nz, max_bin), dtype=np.float32)', content)
        modified = True

    # パターン2: np.zeros((config.nz, nr)) → np.zeros((config.nz, nr), dtype=np.float32)
    pattern2 = r'(np\.zeros\(\(config\.nz,\s*nr\)\))(?!,\s*dtype)'
    if re.search(pattern2, content):
        content = re.sub(pattern2, r'\1, dtype=np.float32', content)
        modified = True

    # パターン3: np.zeros((nz, max_bin)) → np.zeros((nz, max_bin), dtype=np.float32)
    pattern3 = r'(np\.zeros\(\(nz,\s*max_bin\)\))(?!,\s*dtype)'
    if re.search(pattern3, content):
        content = re.sub(pattern3, r'\1, dtype=np.float32', content)
        modified = True

    # パターン4: np.empty((config.nz, ...)) → np.empty((config.nz, ...), dtype=np.float32)
    pattern4 = r'(np\.empty\(\(config\.nz,\s*[^)]+\)\))(?!,\s*dtype)'
    if re.search(pattern4, content):
        content = re.sub(pattern4, r'\1, dtype=np.float32', content)
        modified = True

    if modified and content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Optimized: {filepath}")
        return True
    else:
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python optimize_dtype.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if Path(target).is_file():
        optimize_file(target)
    elif Path(target).is_dir():
        count = 0
        for filepath in Path(target).rglob("*_calc.py"):
            if optimize_file(str(filepath)):
                count += 1
        print(f"\n✅ Total optimized: {count} files")
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
