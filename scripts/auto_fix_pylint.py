"""
pylint問題を自動修正するスクリプト
"""

import re
from pathlib import Path
from typing import List


class PylintAutoFixer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.content = f.read()
        self.lines = self.content.split("\n")

    def remove_unused_imports(self, unused_imports: List[str]) -> None:
        """未使用importを削除"""
        new_lines = []
        for line in self.lines:
            stripped = line.strip()
            should_skip = False

            for unused in unused_imports:
                # "from x import unused" パターン
                if re.match(rf"from .+ import .*\b{re.escape(unused)}\b", stripped):
                    # 複数importの場合は該当部分のみ削除
                    if "," in stripped:
                        line = re.sub(rf",?\s*\b{re.escape(unused)}\b,?\s*", "", line)
                        line = re.sub(r",\s*$", "", line)
                        line = re.sub(r"import\s*,", "import ", line)
                    else:
                        should_skip = True
                # "import unused" パターン
                elif re.match(rf"import\s+{re.escape(unused)}\s*$", stripped):
                    should_skip = True

            if not should_skip and line.strip():
                new_lines.append(line)
            elif not line.strip():
                new_lines.append(line)

        self.lines = new_lines

    def fix_constant_names(self) -> None:
        """定数名をUPPER_CASEに変更（モジュールレベル定数のみ）"""
        constants_to_fix = {}
        function_args = set()  # 関数の引数名を収集
        in_function = False

        # まず全ての関数引数を収集
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("def "):
                # 関数定義から引数を抽出
                match = re.search(r"def\s+\w+\((.*?)\)", stripped)
                if match:
                    args_str = match.group(1)
                    # 引数をカンマで分割して抽出
                    for arg in args_str.split(","):
                        arg = arg.strip()
                        if arg and "=" in arg:
                            arg = arg.split("=")[0].strip()
                        if arg and ":" in arg:
                            arg = arg.split(":")[0].strip()
                        if arg:
                            function_args.add(arg)

        for i, line in enumerate(self.lines):
            stripped = line.strip()

            # 関数/クラス定義の検出
            if stripped.startswith("def ") or stripped.startswith("class "):
                in_function = True
                continue

            # 関数/クラスの外に出たか判定（インデントなしの行）
            if in_function and line and not line[0].isspace():
                in_function = False

            # モジュールレベルの代入文のみ処理
            if not in_function and "=" in stripped and not stripped.startswith("#"):
                match = re.match(r"^([a-z_][a-z0-9_]*)\s*=", stripped)
                if match:
                    var_name = match.group(1)

                    # 除外パターン
                    # 1. 特定の変数名
                    if var_name in ["config", "grid", "vgrid", "mpl_style_sheet"]:
                        continue
                    # 2. 接尾辞による除外
                    if var_name.endswith(("_list", "_env", "_all", "_memmap", "_t")):
                        continue
                    # 3. 接頭辞による除外
                    if var_name.startswith(("data_", "center_", "x_", "y_")):
                        continue
                    # 4. 関数引数名は除外
                    if var_name in function_args:
                        continue
                    # 5. 1文字の変数は除外（ループ変数など: i, j, k, t, z）
                    # ただし物理定数として一般的な L, g などは含める可能性があるため慎重に
                    if len(var_name) == 1 and var_name not in ["g", "L", "f"]:
                        continue

                    # UPPER_CASE化
                    new_name = var_name.upper()
                    if new_name != var_name:
                        constants_to_fix[var_name] = new_name

        # 置換実行（モジュールレベルのみ、かつキーワード引数でない箇所のみ）
        if constants_to_fix:
            new_lines = []
            in_function_block = False

            for line in self.lines:
                stripped = line.strip()

                # 関数/クラスの中かどうか判定
                if stripped.startswith("def ") or stripped.startswith("class "):
                    in_function_block = True
                elif in_function_block and line and not line[0].isspace():
                    in_function_block = False

                # モジュールレベルのみ置換
                if not in_function_block:
                    new_line = line
                    for old, new in constants_to_fix.items():
                        # 2段階で置換:
                        # 1. 代入文の左辺（old = value）を置換
                        new_line = re.sub(
                            rf"^(\s*){re.escape(old)}(\s*=)", rf"\1{new}\2", new_line
                        )
                        # 2. その他の箇所で、キーワード引数（old=value）でない箇所を置換
                        # 行頭の代入でない場合のみ適用
                        if not re.match(rf"^\s*{re.escape(new)}\s*=", new_line):
                            new_line = re.sub(
                                rf"\b{re.escape(old)}\b(?!\s*=)", new, new_line
                            )
                    new_lines.append(new_line)
                else:
                    # 関数内は置換しない
                    new_lines.append(line)

            self.lines = new_lines

    def fix_import_order(self) -> None:
        """import文の順序を修正"""
        docstring_end = 0
        in_docstring = False

        for i, line in enumerate(self.lines):
            stripped = line.strip()
            if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
                in_docstring = True
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    docstring_end = i + 1
                    break
            elif in_docstring and ('"""' in stripped or "'''" in stripped):
                docstring_end = i + 1
                break

        # import文を収集
        imports = {"std": [], "third": [], "local": []}
        import_start = None
        import_end = None

        for i in range(docstring_end, len(self.lines)):
            line = self.lines[i]
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith("import ") or stripped.startswith("from "):
                if import_start is None:
                    import_start = i
                import_end = i

                # 分類
                if stripped.startswith("from .") or "utils." in stripped:
                    imports["local"].append(line)
                elif any(
                    mod in stripped
                    for mod in ["numpy", "matplotlib", "joblib", "scipy", "pandas"]
                ):
                    imports["third"].append(line)
                elif any(
                    mod in stripped
                    for mod in [
                        "os",
                        "sys",
                        "re",
                        "json",
                        "pathlib",
                        "typing",
                        "collections",
                    ]
                ):
                    imports["std"].append(line)
                else:
                    imports["third"].append(line)
            elif stripped and import_start is not None:
                break

        if import_start is None:
            return

        # 並び替え
        new_imports = []
        if imports["std"]:
            new_imports.extend(imports["std"])
            new_imports.append("")
        if imports["third"]:
            new_imports.extend(imports["third"])
            new_imports.append("")
        if imports["local"]:
            new_imports.extend(imports["local"])

        # 再構築
        self.lines = (
            self.lines[:import_start]
            + new_imports
            + [""]
            + self.lines[import_end + 1 :]
        )

    def add_function_docstrings(self) -> None:
        """関数にdocstringを追加"""
        new_lines = []
        i = 0

        while i < len(self.lines):
            line = self.lines[i]
            new_lines.append(line)

            stripped = line.strip()
            if stripped.startswith("def ") and "(" in stripped:
                func_name = stripped.split("(")[0].replace("def ", "").strip()
                indent = len(line) - len(line.lstrip())

                if i + 1 < len(self.lines):
                    next_line = self.lines[i + 1].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        docstring = (
                            " " * (indent + 4) + f'"""{func_name}の処理を実行"""'
                        )
                        new_lines.append(docstring)

            i += 1

        self.lines = new_lines

    def fix_f_strings(self) -> None:
        """補間のないf-stringを修正"""
        new_lines = []

        for line in self.lines:

            def replace_f_string(match):
                quote = match.group(1)
                content = match.group(2)
                if "{" not in content:
                    return f"{quote}{content}{quote}"
                return match.group(0)

            new_line = re.sub(r'f(["\'])((?:(?!\1).)*?)\1', replace_f_string, line)
            new_lines.append(new_line)

        self.lines = new_lines

    def add_module_docstring(self) -> None:
        """モジュールdocstringを追加"""
        if self.lines and (
            self.lines[0].strip().startswith('"""')
            or self.lines[0].strip().startswith("'''")
        ):
            return

        module_name = self.file_path.stem.replace("_", " ")
        docstring = f'"""\n{module_name}\n"""\n'
        self.lines = docstring.split("\n") + self.lines

    def save(self) -> None:
        """ファイルに保存"""
        content = "\n".join(self.lines)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Fixed: {self.file_path}")


def fix_file(file_path: str, issues: dict):
    """ファイルを自動修正"""
    fixer = PylintAutoFixer(file_path)

    if issues.get("unused_imports"):
        fixer.remove_unused_imports(issues["unused_imports"])

    if issues.get("missing_module_docstring"):
        fixer.add_module_docstring()

    if issues.get("import_order"):
        fixer.fix_import_order()

    if issues.get("naming"):
        fixer.fix_constant_names()

    if issues.get("f_string"):
        fixer.fix_f_strings()

    # 関数docstringは自動追加しない（無意味なdocstringになるため）
    # if issues.get('missing_function_docstrings'):
    #     fixer.add_function_docstrings()

    fixer.save()
