#!/usr/bin/env python3
"""
ファイル移行支援スクリプト

既存の解析スクリプトを新しいutils/モジュールを使用するように
移行するための支援ツールです。

使用方法:
    python scripts/migrate_helper.py <file_path>
"""

import sys
from pathlib import Path


def analyze_file(filepath: Path) -> dict:
    """
    ファイルを分析して、移行可能な箇所を特定

    Args:
        filepath: 分析対象のファイルパス

    Returns:
        dict: 分析結果
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    analysis = {
        "file": str(filepath),
        "has_config_loading": False,
        "has_grid_calculation": False,
        "has_match_statement": False,
        "has_style_parsing": False,
        "line_count": len(content.split("\n")),
        "suggestions": [],
    }

    # 設定読み込みの検出
    if "with open('setting.json'" in content or 'with open("setting.json"' in content:
        analysis["has_config_loading"] = True
        analysis["suggestions"].append(
            "✓ 設定読み込みを AnalysisConfig() に置き換え可能（約20-30行削減）"
        )

    # グリッド計算の検出
    if "np.meshgrid" in content and "np.arctan2" in content:
        analysis["has_grid_calculation"] = True
        analysis["suggestions"].append(
            "✓ グリッド計算を GridHandler に置き換え可能（約10-15行削減）"
        )

    # match文の検出
    if "match varname:" in content or "match " in content:
        match_count = content.count("case ")
        analysis["has_match_statement"] = True
        analysis["suggestions"].append(
            f"✓ match文（{match_count}個のcase）を PlotConfig に置き換え可能（大幅削減）"
        )

    # スタイル解析の検出
    if "len(sys.argv)" in content and "mpl_style_sheet" in content:
        analysis["has_style_parsing"] = True
        analysis["suggestions"].append(
            "✓ スタイル解析を parse_style_argument() に置き換え可能（約5行削減）"
        )

    # 期待される削減行数を計算
    expected_reduction = 0
    if analysis["has_config_loading"]:
        expected_reduction += 25
    if analysis["has_grid_calculation"]:
        expected_reduction += 12
    if analysis["has_match_statement"]:
        expected_reduction += match_count * 8  # 各caseあたり約8行
    if analysis["has_style_parsing"]:
        expected_reduction += 5

    analysis["expected_reduction"] = expected_reduction
    analysis["expected_line_count"] = max(
        analysis["line_count"] - expected_reduction, 20
    )

    return analysis


def generate_migration_template(analysis: dict) -> str:
    """
    移行テンプレートを生成

    Args:
        analysis: analyze_file()の結果

    Returns:
        str: 移行テンプレート
    """
    template = []
    template.append("# 移行後のコード例:\n")
    template.append("```python")
    template.append("import os")
    template.append("import sys")
    template.append("script_dir = os.path.dirname(os.path.abspath(__file__))")
    template.append("sys.path.append(os.path.join(script_dir, '..'))")
    template.append("")
    template.append("import numpy as np")

    imports = []
    if analysis["has_config_loading"]:
        imports.append("from utils.config import AnalysisConfig")
    if analysis["has_grid_calculation"]:
        imports.append("from utils.grid import GridHandler")
    if analysis["has_match_statement"] or analysis["has_style_parsing"]:
        imports.append("from utils.plotting import PlotConfig, parse_style_argument")

    template.extend(imports)
    template.append("")

    if analysis["has_config_loading"]:
        template.append("# 設定とグリッドの初期化")
        template.append("config = AnalysisConfig()")

    if analysis["has_grid_calculation"]:
        template.append("grid = GridHandler(config)")

    if analysis["has_style_parsing"]:
        template.append("mpl_style_sheet = parse_style_argument()")

    template.append("")
    template.append("# ... 残りのコード ...")
    template.append("```")

    return "\n".join(template)


def print_analysis_report(analysis: dict):
    """分析レポートを表示"""
    print("\n" + "=" * 70)
    print(f"📄 ファイル: {analysis['file']}")
    print("=" * 70)
    print(f"\n📊 現在の行数: {analysis['line_count']}行")
    print(f"📉 期待削減: 約{analysis['expected_reduction']}行")
    print(f"📈 移行後予想: 約{analysis['expected_line_count']}行")
    print(
        f"💾 削減率: {analysis['expected_reduction'] / analysis['line_count'] * 100:.1f}%"
    )

    print("\n🔍 検出された移行可能箇所:")
    if not analysis["suggestions"]:
        print("  なし（このファイルは移行の必要がないか、既に移行済みです）")
    else:
        for suggestion in analysis["suggestions"]:
            print(f"  {suggestion}")

    print("\n" + "=" * 70)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python migrate_helper.py <file_path>")
        print("\n例:")
        print(
            "  python scripts/migrate_helper.py 3d/relative_wind_radial_tangential_calc.py"
        )
        print("  python scripts/migrate_helper.py 2d/whole_domain.py")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"エラー: ファイル '{filepath}' が見つかりません")
        sys.exit(1)

    # ファイルを分析
    analysis = analyze_file(filepath)

    # レポートを表示
    print_analysis_report(analysis)

    # テンプレートを生成
    if analysis["suggestions"]:
        print("\n💡 移行テンプレート:")
        print(generate_migration_template(analysis))

        print("\n📚 詳細な移行手順は MIGRATION_GUIDE.md を参照してください")


if __name__ == "__main__":
    main()
