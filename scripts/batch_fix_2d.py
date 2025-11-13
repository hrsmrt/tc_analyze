"""
2dディレクトリのPythonファイルを一括でスタイル修正するスクリプト
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from auto_fix_pylint import PylintAutoFixer

# 2dディレクトリのパス
BASE_DIR = Path(__file__).parent.parent / "2d"

# 修正対象のファイルリスト
FILES_TO_FIX = [
    "ss_wind10m_abs_vortex_region.py",
    "ss_wind10m_abs_vortex_region2.py",
    "ss_wind10m_abs_whole_domain.py",
    "ss_wind10m_tangential_plot.py",
    "whole_domain_with_center_plot.py",
    "whole_domain_with_low2_plot.py",
    "y_ave.py",
]


def main():
    """メイン処理"""
    print("2dディレクトリのスタイル修正を開始します...")

    for filename in FILES_TO_FIX:
        filepath = BASE_DIR / filename

        if not filepath.exists():
            print(f"⚠️  スキップ: {filename} (ファイルが存在しません)")
            continue

        print(f"\n処理中: {filename}")

        try:
            fixer = PylintAutoFixer(str(filepath))

            # import順序の修正
            if fixer.fix_import_order():
                print(f"  ✓ import順序を修正しました")

            # 未使用importの削除
            removed = fixer.remove_unused_imports()
            if removed:
                print(f"  ✓ 未使用import削除: {', '.join(removed)}")

            # 定数名の修正
            fixed = fixer.fix_constant_names()
            if fixed:
                print(f"  ✓ 定数名修正: {len(fixed)}個")

            # f-stringの修正
            if fixer.fix_f_strings():
                print(f"  ✓ f-stringを修正しました")

            # モジュールdocstringの追加
            if fixer.add_module_docstring():
                print(f"  ✓ モジュールdocstringを追加しました")

            print(f"✅ 完了: {filename}")

        except Exception as e:
            print(f"❌ エラー: {filename} - {str(e)}")
            continue

    print("\n" + "=" * 50)
    print("2dディレクトリのスタイル修正が完了しました")


if __name__ == "__main__":
    main()
