#!/usr/bin/env python3
"""
range(config.nt)をrange(config.t_first, config.t_last)に置換するスクリプト
"""
import re
import sys
from pathlib import Path


def update_time_range(file_path):
    """ファイル内のrange(config.nt)をrange(config.t_first, config.t_last)に置換"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # range(config.nt) を range(config.t_first, config.t_last) に置換
        content = re.sub(
            r"range\(config\.nt\)", "range(config.t_first, config.t_last)", content
        )

        # range(0,config.nt,step) を range(config.t_first,config.t_last,step) に置換
        content = re.sub(
            r"range\(0,\s*config\.nt,", "range(config.t_first, config.t_last,", content
        )

        # range(0,config.nt) を range(config.t_first,config.t_last) に置換
        content = re.sub(
            r"range\(0,\s*config\.nt\)", "range(config.t_first, config.t_last)", content
        )

        # range(config.nt-...,config.nt) を range(config.t_last-...,config.t_last) に置換
        content = re.sub(r"range\(config\.nt-", "range(config.t_last-", content)

        # 変更があった場合のみ書き込み
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
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
    target_dirs = [
        "center",
        "3d",
        "2d",
        "azim_mean",
        "z_profile",
        "z_profile_q4",
        "symmetrisity",
        "specific",
    ]

    modified_count = 0
    total_count = 0

    for target_dir in target_dirs:
        dir_path = project_root / target_dir
        if not dir_path.exists():
            continue

        # 全ての.pyファイルを処理
        for py_file in dir_path.rglob("*.py"):
            # __pycache__は除外
            if "__pycache__" in str(py_file):
                continue

            total_count += 1
            if update_time_range(py_file):
                modified_count += 1
                print(f"Modified: {py_file.relative_to(project_root)}")

    print(f"\nTotal: {total_count} files checked, {modified_count} files modified")


if __name__ == "__main__":
    main()
