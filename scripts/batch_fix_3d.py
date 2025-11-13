"""
3d/ディレクトリの全ファイルを一括自動修正
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

# 同じディレクトリのauto_fix_pylint.pyをインポート
from auto_fix_pylint import fix_file


def parse_pylint_log(log_path: str, directory_filter: str = "3d"):
    """pylint.logを解析してファイルごとの問題を抽出"""
    issues_by_file = defaultdict(
        lambda: {
            "unused_imports": [],
            "missing_module_docstring": False,
            "missing_function_docstrings": False,
            "naming": [],
            "import_order": False,
            "f_string": False,
        }
    )

    with open(log_path, "r") as f:
        lines = f.readlines()

    current_file = None
    for line in lines:
        if f"************* Module {directory_filter}." in line:
            module = line.split("Module ")[1].strip()
            filename = module.replace(".", "/") + ".py"
            current_file = filename

        elif current_file and current_file.startswith(f"{directory_filter}/"):
            # 未使用import
            if "W0611" in line and "unused-import" in line:
                match = re.search(r"Unused (.+?) imported", line)
                if match:
                    import_name = match.group(1)
                    issues_by_file[current_file]["unused_imports"].append(import_name)

            # モジュールdocstring欠如
            elif "C0114" in line:
                issues_by_file[current_file]["missing_module_docstring"] = True

            # 関数docstring欠如
            elif "C0116" in line:
                issues_by_file[current_file]["missing_function_docstrings"] = True

            # 定数の命名規則
            elif "C0103" in line and "Constant name" in line:
                match = re.search(r'Constant name "(.+?)"', line)
                if match:
                    var_name = match.group(1)
                    issues_by_file[current_file]["naming"].append(var_name)

            # import順序
            elif "C0411" in line:
                issues_by_file[current_file]["import_order"] = True

            # f-string without interpolation
            elif "W1309" in line:
                issues_by_file[current_file]["f_string"] = True

    return issues_by_file


def main():
    """メイン処理"""
    base_path = Path(__file__).parent.parent  # tc_analyze/
    log_path = base_path / "pylint.log"

    # pylint.logを解析
    print("Parsing pylint.log...")
    issues = parse_pylint_log(str(log_path), directory_filter="3d")

    print(f"\nFound {len(issues)} files with issues in 3d/")

    # 除外ファイル（問題が多すぎるファイル）
    exclude_files = [
        "3d/ms_wind_radial_plot.py",
        "3d/whole_domain copy.py",
    ]

    # 各ファイルを修正
    fixed_count = 0
    for filepath, file_issues in sorted(issues.items()):
        if filepath in exclude_files:
            print(f"⊘ Skipped: {filepath} (excluded)")
            continue

        full_path = base_path / filepath
        if not full_path.exists():
            print(f"⊘ Skipped: {filepath} (not found)")
            continue

        # 問題がない場合はスキップ
        has_issues = any(
            [
                file_issues["unused_imports"],
                file_issues["missing_module_docstring"],
                file_issues["missing_function_docstrings"],
                file_issues["naming"],
                file_issues["import_order"],
                file_issues["f_string"],
            ]
        )

        if not has_issues:
            continue

        try:
            print(f"Fixing: {filepath}")
            fix_file(str(full_path), file_issues)
            fixed_count += 1
        except Exception as e:
            print(f"✗ Error fixing {filepath}: {e}")

    print(f"\n{'='*50}")
    print(f"Summary: Fixed {fixed_count} files in 3d/")


if __name__ == "__main__":
    main()
