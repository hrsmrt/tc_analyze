#!/usr/bin/env python3
"""
自動ファイル移行スクリプト

既存の解析スクリプトを自動的に新しいutils/モジュールを使用するように変換します。
"""

import re
import shutil
import sys
from pathlib import Path
from typing import Tuple


def backup_file(filepath: Path) -> Path:
    """ファイルをバックアップ"""
    backup_path = filepath.with_suffix(filepath.suffix + ".backup")
    shutil.copy2(filepath, backup_path)
    return backup_path


def add_imports(content: str, filepath: Path) -> str:
    """必要なインポートを追加"""
    # ファイルの階層を判定
    depth = len(filepath.parent.parts)
    parent_path = "../" * (depth - 1) if depth > 1 else ".."

    # 既存のインポートセクションを見つける
    lines = content.split("\n")

    # shebang, docstring, import行の後にインポートを追加
    insert_pos = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # shebangをスキップ
        if stripped.startswith("#!"):
            insert_pos = i + 1
            continue

        # docstringの開始/終了を検出
        if '"""' in stripped or "'''" in stripped:
            if not in_docstring:
                in_docstring = True
                docstring_char = '"""' if '"""' in stripped else "'''"
                # 同じ行で閉じている場合
                if stripped.count(docstring_char) >= 2:
                    in_docstring = False
                    insert_pos = i + 1
            elif docstring_char in stripped:
                in_docstring = False
                insert_pos = i + 1
            continue

        if in_docstring:
            continue

        # import行を見つける
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_pos = i + 1
            continue

        # 空行やコメントをスキップ
        if not stripped or stripped.startswith("#"):
            if insert_pos == i:
                insert_pos = i + 1
            continue

        # コード開始
        break

    # sys.pathの追加が必要かチェック
    has_syspath = "sys.path.append" in content
    has_utils_import = "from utils" in content

    if has_utils_import:
        return content  # 既に移行済み

    # 新しいインポートを構築
    new_imports = []

    if not has_syspath:
        new_imports.extend(
            [
                "import sys",
                "import os",
                "script_dir = os.path.dirname(os.path.abspath(__file__))",
                f'sys.path.append(os.path.join(script_dir, "{parent_path}"))',
                "",
            ]
        )

    # utils からのインポートを追加
    imports_to_add = []

    if "with open('setting.json'" in content or 'with open("setting.json"' in content:
        imports_to_add.append("from utils.config import AnalysisConfig")

    if "np.meshgrid" in content:
        imports_to_add.append("from utils.grid import GridHandler")

    if "match varname:" in content or (
        "len(sys.argv)" in content and "mpl_style" in content
    ):
        imports_to_add.append(
            "from utils.plotting import PlotConfig, parse_style_argument, create_custom_colormap"
        )

    if imports_to_add:
        new_imports.extend(imports_to_add)
        new_imports.append("")

    # インポートを挿入
    if new_imports:
        lines.insert(insert_pos, "\n".join(new_imports))

    return "\n".join(lines)


def replace_config_loading(content: str) -> str:
    """設定読み込みコードを置き換え"""

    # 設定読み込みパターン
    config_pattern = r"""# ファイルを開いてJSONを読み込む\n.*?with open\(['"](\.\.\/)?setting\.json['"],.*?\) as f:.*?
.*?setting = json\.load\(f\).*?
.*?glevel = setting\[['"]glevel['"]\].*?
.*?nt = setting\[['"]nt['"]\].*?
.*?dt = setting\[['"]dt_output['"]\].*?
.*?dt_hour = int\(dt / 3600\).*?
.*?triangle_size = setting\[['"]triangle_size['"]\].*?
.*?nx = 2 \*\* glevel.*?
.*?ny = 2 \*\* glevel.*?
(?:.*?nz = (?:setting\[['"]nz['"]\]|74).*?)?.*?x_width = triangle_size.*?
.*?y_width = triangle_size \* 0\.5 \* 3\.0 ?\*\* ?0\.5.*?
.*?dx = x_width / nx.*?
.*?dy = y_width / ny.*?
(?:.*?input_folder = setting\[['"]input_folder['"]\].*?)?"""

    # より簡潔なパターン
    simple_pattern = (
        r"with open\(['\"].*?setting\.json['\"].*?\).*?[\s\S]*?(?=\n(?:[a-zA-Z_]|#|$))"
    )

    replacement = """# 設定とグリッドの初期化
config = AnalysisConfig()"""

    # まず複雑なパターンを試す
    new_content = re.sub(
        config_pattern, replacement, content, flags=re.MULTILINE | re.DOTALL
    )

    if new_content == content:
        # 簡略版を試す
        if (
            "with open('setting.json'" in content
            or 'with open("setting.json"' in content
        ):
            # 個別に置き換え
            new_content = re.sub(
                r"with open\(['\"]setting\.json['\"].*?\).*?as f:.*?\n.*?setting = json\.load\(f\)",
                "# 設定読み込み（下記で config = AnalysisConfig() に置き換え）",
                content,
            )

    # 変数参照を置き換え
    replacements = {
        r"\bglevel\b": "config.glevel",
        r"\bnt\b": "config.nt",
        r"\bdt_hour\b": "config.dt_hour",
        r"\btriangle_size\b": "config.triangle_size",
        r"\bnx\b": "config.nx",
        r"\bny\b": "config.ny",
        r"\bnz\b": "config.nz",
        r"\bx_width\b": "config.x_width",
        r"\by_width\b": "config.y_width",
        r"\bdx\b": "config.dx",
        r"\bdy\b": "config.dy",
        r"\binput_folder\b": "config.input_folder",
        r"\btime_list\b": "config.time_list",
        r"\bvgrid_filepath\b": "config.vgrid_filepath",
        r"setting\[['\"]+vgrid_filepath['\"]+ ?\]": "config.vgrid_filepath",
    }

    for pattern, replacement in replacements.items():
        new_content = re.sub(pattern, replacement, new_content)

    # config = AnalysisConfig() を追加（まだない場合）
    if "AnalysisConfig()" not in new_content and "setting.json" in content:
        # import文の後に追加
        new_content = re.sub(
            r"(from utils\.config import AnalysisConfig\n)",
            r"\1\n# 設定の初期化\nconfig = AnalysisConfig()\n",
            new_content,
        )

    return new_content


def replace_grid_calculation(content: str) -> str:
    """グリッド計算コードを置き換え"""

    # メッシュグリッド生成パターン
    meshgrid_patterns = [
        r"x = \(np\.arange\(nx\) \+ 0\.5\) \* dx\n.*?y = \(np\.arange\(ny\) \+ 0\.5\) \* dy\n.*?X,\s*Y = np\.meshgrid\(x,\s*y\)",
        r"x = np\.arange\(0,\s*x_width,\s*dx\).*?\n.*?y = np\.arange\(0,\s*y_width,\s*dy\).*?\n.*?X,\s*Y = np\.meshgrid\(x,\s*y\)",
    ]

    grid_init = "grid = GridHandler(config)"

    for pattern in meshgrid_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, grid_init, content)
            break

    # GridHandler を使用する場合の変数置き換え
    if "GridHandler" in content:
        content = re.sub(r"\bX\b(?![\w])", "grid.X", content)
        content = re.sub(r"\bY\b(?![\w])", "grid.Y", content)
        content = re.sub(r"grid\.grid\.(X|Y)", r"grid.\1", content)  # 二重参照を修正

    # 周期境界条件と角度計算を uv_to_radial_tangential に置き換え
    radial_tangential_pattern = r"""dX = X - c[xy].*?
.*?dY = Y - c[xy].*?
.*?dX\[dX > 0\.5 \* x_width\] -= x_width.*?
.*?dX\[dX < -0\.5 \* x_width\] \+= x_width.*?
.*?theta = np\.arctan2\(dY,\s*dX\).*?
(?:.*?\n)*?.*?v_radial = data_u \* np\.cos\(theta\) \+ data_v \* np\.sin\(theta\).*?
.*?v_tangential = -data_u \* np\.sin\(theta\) \+ data_v \* np\.cos\(theta\)"""

    if re.search(radial_tangential_pattern, content, flags=re.MULTILINE | re.DOTALL):
        # cx, cy を取得
        content = re.sub(
            radial_tangential_pattern,
            "# 直交座標系から極座標系への変換\n    v_radial, v_tangential = grid.uv_to_radial_tangential(data_u, data_v, cx, cy)",
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

    return content


def replace_style_parsing(content: str) -> str:
    """スタイル解析コードを置き換え"""

    style_pattern = r"""# コマンドライン引数が.*?あるかを確認.*?
if len\(sys\.argv\) > \d+:.*?
.*?mpl_style_sheet = sys\.argv\[\d+\].*?
.*?print\(f?['"]+Using style:.*?\).*?
else:.*?
.*?print\(['"]+No style sheet specified.*?\)"""

    replacement = """# スタイルシートの解析
mpl_style_sheet = parse_style_argument()"""

    return re.sub(style_pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)


def add_docstring(content: str, filepath: Path) -> str:
    """ファイルの先頭にdocstringを追加"""

    lines = content.split("\n")

    # 既にdocstringがあるかチェック
    for line in lines[:10]:
        if '"""' in line or "'''" in line:
            return content  # 既にある

    # ファイル名から説明を生成
    filename = filepath.stem

    # 説明を生成
    if "_calc" in filename:
        desc = f"{filename.replace('_calc', '')} の計算\n\n計算処理を実行します。"
    elif "_plot" in filename:
        desc = (
            f"{filename.replace('_plot', '')} のプロット\n\nプロット処理を実行します。"
        )
    else:
        desc = f"{filename}\n\n解析処理を実行します。"

    # shebangの後に挿入
    insert_pos = 1 if lines[0].startswith("#!") else 0

    docstring = f'"""\n{desc}\n"""\n'
    lines.insert(insert_pos, docstring)

    return "\n".join(lines)


def migrate_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    ファイルを移行

    Returns:
        (success, message)
    """
    try:
        # ファイルを読み込み
        with open(filepath, "r", encoding="utf-8") as f:
            original_content = f.read()

        # 変換を適用
        content = original_content
        content = add_docstring(content, filepath)
        content = add_imports(content, filepath)
        content = replace_config_loading(content)
        content = replace_grid_calculation(content)
        content = replace_style_parsing(content)

        # 変更がない場合
        if content == original_content:
            return True, "変更なし（既に移行済みまたは移行不要）"

        if dry_run:
            return True, f"変更あり（{len(content) - len(original_content):+d} 文字）"

        # バックアップ
        backup_path = backup_file(filepath)

        # ファイルを書き込み
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # 構文チェック
        import py_compile

        try:
            py_compile.compile(str(filepath), doraise=True)
        except py_compile.PyCompileError as e:
            # エラーがあれば復元
            shutil.copy2(backup_path, filepath)
            return False, f"構文エラー: {e}"

        return True, f"成功（バックアップ: {backup_path.name}）"

    except Exception as e:
        return False, f"エラー: {e}"


def main():
    if len(sys.argv) < 2:
        print("使用方法: python auto_migrate.py <file_or_directory> [--dry-run]")
        print("\n例:")
        print("  python scripts/auto_migrate.py 3d/cape.py")
        print("  python scripts/auto_migrate.py 3d/")
        print("  python scripts/auto_migrate.py 3d/ --dry-run")
        sys.exit(1)

    target = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("🔍 ドライランモード（実際の変更は行いません）\n")

    # ファイルリストを取得
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.glob("**/*.py"))
    else:
        print(f"エラー: '{target}' が見つかりません")
        sys.exit(1)

    # 各ファイルを処理
    success_count = 0
    skip_count = 0
    error_count = 0

    for filepath in files:
        print(f"処理中: {filepath}")
        success, message = migrate_file(filepath, dry_run)

        if success:
            if "変更なし" in message:
                print(f"  ⏭️  {message}")
                skip_count += 1
            else:
                print(f"  ✅ {message}")
                success_count += 1
        else:
            print(f"  ❌ {message}")
            error_count += 1
        print()

    # サマリー
    print("=" * 70)
    print(f"処理完了: {len(files)} ファイル")
    print(f"  成功: {success_count}")
    print(f"  スキップ: {skip_count}")
    print(f"  エラー: {error_count}")
    print("=" * 70)

    if not dry_run and success_count > 0:
        print("\n💡 ヒント: バックアップファイル (*.backup) は動作確認後に削除できます")


if __name__ == "__main__":
    main()
