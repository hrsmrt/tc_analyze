#!/usr/bin/env python3
"""
parse_style_argument()からarg_indexパラメータを削除するスクリプト
"""
import re
import sys
from pathlib import Path

def remove_arg_index(file_path):
    """ファイル内のparse_style_argument(arg_index=N)をparse_style_argument()に置換"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # parse_style_argument(arg_index=数字) を parse_style_argument() に置換
        original_content = content
        content = re.sub(
            r'parse_style_argument\(arg_index=\d+\)',
            'parse_style_argument()',
            content
        )

        # 変更があった場合のみ書き込み
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """メイン処理"""
    # プロジェクトルート
    project_root = Path(__file__).parent.parent.parent

    # 対象ディレクトリ
    target_dirs = ['center', '3d', '2d', 'azim_mean', 'z_profile', 'symmetrisity']

    modified_count = 0
    total_count = 0

    for target_dir in target_dirs:
        dir_path = project_root / target_dir
        if not dir_path.exists():
            continue

        # 全ての.pyファイルを処理
        for py_file in dir_path.rglob('*.py'):
            total_count += 1
            if remove_arg_index(py_file):
                modified_count += 1
                print(f"Modified: {py_file.relative_to(project_root)}")

    print(f"\nTotal: {total_count} files checked, {modified_count} files modified")

if __name__ == '__main__':
    main()
