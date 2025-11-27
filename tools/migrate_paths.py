#!/usr/bin/env python3
"""
パス設定を一括で移行するスクリプト

./data/ と ./fig/ のハードコードされたパスを
config.get_data_path() と config.get_fig_path() に変換します。
"""
import os
import re
import sys
from pathlib import Path


def parse_path_components(path_str):
    """
    パス文字列から構成要素を抽出

    例: "./data/3d/psi/" -> ["3d", "psi"]
    """
    # Remove leading ./ and trailing /
    clean_path = path_str.strip('"\'').strip('./').strip('/')

    # Split by /
    components = [c for c in clean_path.split('/') if c and c not in ['data', 'fig']]

    return components


def convert_data_path(match):
    """./data/xxx/yyy/ を config.get_data_path("xxx", "yyy") に変換"""
    full_match = match.group(0)
    path_part = match.group(1)  # ./data/ の後の部分

    # パスの終端を確認
    if path_part.endswith('/'):
        path_part = path_part[:-1]

    components = [c for c in path_part.split('/') if c]

    if not components:
        return 'config.get_data_path()'

    # 引数リストを作成
    args = ', '.join(f'"{c}"' for c in components)
    return f'config.get_data_path({args})'


def convert_fig_path(match):
    """./fig/xxx/yyy/ を config.get_fig_path("xxx", "yyy") に変換"""
    full_match = match.group(0)
    path_part = match.group(1)  # ./fig/ の後の部分

    # パスの終端を確認
    if path_part.endswith('/'):
        path_part = path_part[:-1]

    components = [c for c in path_part.split('/') if c]

    if not components:
        return 'config.get_fig_path()'

    # 引数リストを作成
    args = ', '.join(f'"{c}"' for c in components)
    return f'config.get_fig_path({args})'


def migrate_file(file_path, dry_run=False):
    """
    ファイル内のパスを移行

    Args:
        file_path: 対象ファイルのパス
        dry_run: Trueの場合は変更せずに表示のみ

    Returns:
        変更があったかどうか
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # パターン1: "./data/xxx/yyy/" の形式
    # FOLDER = "./data/3d/psi/" のようなケース
    content = re.sub(
        r'"\.\/data\/([^"]+)"',
        convert_data_path,
        content
    )

    # パターン2: "./fig/xxx/yyy/" の形式
    content = re.sub(
        r'"\.\/fig\/([^"]+)"',
        convert_fig_path,
        content
    )

    # パターン3: f"./data/xxx/yyy/file{var}.ext" のようなf-string
    # これは複雑なので個別対応が必要

    if content != original_content:
        if dry_run:
            print(f"[DRY RUN] Would modify: {file_path}")
            # 差分を表示
            lines_before = original_content.split('\n')
            lines_after = content.split('\n')
            for i, (before, after) in enumerate(zip(lines_before, lines_after), 1):
                if before != after:
                    print(f"  Line {i}:")
                    print(f"    - {before}")
                    print(f"    + {after}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Modified: {file_path}")
        return True
    else:
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Migrate hardcoded paths to config methods')
    parser.add_argument('paths', nargs='+', help='Files or directories to migrate')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')
    parser.add_argument('--pattern', default='*.py', help='File pattern to match (default: *.py)')

    args = parser.parse_args()

    files_to_process = []

    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file():
            files_to_process.append(path)
        elif path.is_dir():
            files_to_process.extend(path.glob(args.pattern))
        else:
            print(f"Warning: {path_str} not found", file=sys.stderr)

    if not files_to_process:
        print("No files to process")
        return

    print(f"Processing {len(files_to_process)} files...")
    if args.dry_run:
        print("[DRY RUN MODE - No files will be modified]")
    print()

    modified_count = 0
    for file_path in sorted(files_to_process):
        if migrate_file(file_path, dry_run=args.dry_run):
            modified_count += 1

    print()
    print(f"{'Would modify' if args.dry_run else 'Modified'} {modified_count}/{len(files_to_process)} files")


if __name__ == '__main__':
    main()
