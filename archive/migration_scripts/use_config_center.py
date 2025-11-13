#!/usr/bin/env python3
"""
np.loadtxt("./data/ss_slp_center_x.txt")をconfig.center_xに置換するスクリプト
"""
import re
import sys
from pathlib import Path


def replace_center_loadtxt(file_path):
    """ファイル内のcenter座標読み込みをconfig経由に変更"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # パターン1: center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
        content = re.sub(
            r'center_x_list\s*=\s*np\.loadtxt\(["\']\./data/ss_slp_center_x\.txt["\']\s*(?:,\s*ndmin=1)?\)',
            "center_x_list = config.center_x",
            content,
        )

        content = re.sub(
            r'center_y_list\s*=\s*np\.loadtxt\(["\']\./data/ss_slp_center_y\.txt["\']\s*(?:,\s*ndmin=1)?\)',
            "center_y_list = config.center_y",
            content,
        )

        # パターン1b: center_x_list = np.loadtxt("data/ss_slp_center_x.txt")
        content = re.sub(
            r'center_x_list\s*=\s*np\.loadtxt\(["\']data/ss_slp_center_x\.txt["\']\s*(?:,\s*ndmin=1)?\)',
            "center_x_list = config.center_x",
            content,
        )

        content = re.sub(
            r'center_y_list\s*=\s*np\.loadtxt\(["\']data/ss_slp_center_y\.txt["\']\s*(?:,\s*ndmin=1)?\)',
            "center_y_list = config.center_y",
            content,
        )

        # パターン2: x_c_evo = np.loadtxt("data/ss_slp_center_x.txt")
        content = re.sub(
            r'x_c_evo\s*=\s*np\.loadtxt\(["\']data/ss_slp_center_x\.txt["\']\s*(?:,\s*ndmin=1)?\)',
            "x_c_evo = config.center_x",
            content,
        )

        content = re.sub(
            r'y_c_evo\s*=\s*np\.loadtxt\(["\']data/ss_slp_center_y\.txt["\']\s*(?:,\s*ndmin=1)?\)',
            "y_c_evo = config.center_y",
            content,
        )

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
        "sums",
        "azim_q8",
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
            if replace_center_loadtxt(py_file):
                modified_count += 1
                print(f"Modified: {py_file.relative_to(project_root)}")

    print(f"\nTotal: {total_count} files checked, {modified_count} files modified")


if __name__ == "__main__":
    main()
