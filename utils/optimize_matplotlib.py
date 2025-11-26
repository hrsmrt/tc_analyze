#!/usr/bin/env python
"""
Matplotlibバックエンド最適化スクリプト

プロットファイルにmatplotlib.use('Agg')を追加して、
GUI描画のオーバーヘッドを削減します。
"""

import os
import sys
from pathlib import Path


def optimize_file(filepath):
    """ファイルにMatplotlibバックエンド最適化を適用"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 既に最適化済みかチェック
    has_agg = any("matplotlib.use('Agg')" in line or 'matplotlib.use("Agg")' in line for line in lines)
    if has_agg:
        print(f"Already optimized: {filepath}")
        return False

    # import matplotlib.pyplot as pltの行を探す
    new_lines = []
    modified = False

    for i, line in enumerate(lines):
        if not modified and 'import matplotlib.pyplot as plt' in line:
            # この行の前にmatplotlib.use('Agg')を挿入
            new_lines.append("import matplotlib\n")
            new_lines.append("matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減\n")
            new_lines.append(line)
            modified = True
        else:
            new_lines.append(line)

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✅ Optimized: {filepath}")
        return True
    else:
        print(f"⚠️  No matplotlib.pyplot import found: {filepath}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python optimize_matplotlib.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        # 単一ファイルを最適化
        optimize_file(target)
    elif os.path.isdir(target):
        # ディレクトリ内の全プロットファイルを最適化
        count = 0
        for filepath in Path(target).rglob("*plot*.py"):
            if optimize_file(str(filepath)):
                count += 1
        print(f"\n✅ Total optimized: {count} files")
    else:
        print(f"Error: {target} is not a file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
