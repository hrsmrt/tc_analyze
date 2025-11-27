#!/usr/bin/env python3
"""
Analyze current project structure
"""
from pathlib import Path
from collections import defaultdict

root = Path("/Users/hiroshimurata/tc_analyze")

# 除外ディレクトリ
exclude = {".git", "__pycache__", "tc_analyze.egg-info", "archive"}

# 統計情報
stats = defaultdict(lambda: {"py": 0, "sh": 0, "subdirs": [], "calc": 0, "plot": 0})

# トップレベルディレクトリを走査
for item in sorted(root.iterdir()):
    if not item.is_dir() or item.name in exclude or item.name.startswith("."):
        continue

    dir_name = item.name

    # Pythonファイル数
    py_files = list(item.glob("*.py"))
    stats[dir_name]["py"] = len(py_files)

    # calc/plotの分類
    for f in py_files:
        if "_calc.py" in f.name:
            stats[dir_name]["calc"] += 1
        elif "_plot.py" in f.name or "plot" in f.name:
            stats[dir_name]["plot"] += 1

    # シェルスクリプト数
    stats[dir_name]["sh"] = len(list(item.glob("*.sh")))

    # サブディレクトリ
    subdirs = [d.name for d in item.iterdir() if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__"]
    stats[dir_name]["subdirs"] = subdirs

# 結果出力
print("=" * 80)
print("プロジェクト構造分析")
print("=" * 80)
print()
print(f"{'Directory':<20} {'Py files':<12} {'Calc':<8} {'Plot':<8} {'Shell':<8} {'Subdirs'}")
print("-" * 80)

total_py = 0
total_calc = 0
total_plot = 0

for dir_name in sorted(stats.keys()):
    s = stats[dir_name]
    total_py += s["py"]
    total_calc += s["calc"]
    total_plot += s["plot"]

    subdirs_str = ", ".join(s["subdirs"][:3])
    if len(s["subdirs"]) > 3:
        subdirs_str += f", ... ({len(s['subdirs'])} total)"

    print(f"{dir_name:<20} {s['py']:<12} {s['calc']:<8} {s['plot']:<8} {s['sh']:<8} {subdirs_str}")

print("-" * 80)
print(f"{'TOTAL':<20} {total_py:<12} {total_calc:<8} {total_plot:<8}")
print()

# サブディレクトリの詳細（azim_meanなど）
print("=" * 80)
print("サブディレクトリの詳細")
print("=" * 80)

for dir_name in ["azim_mean", "3d", "2d"]:
    dir_path = root / dir_name
    if not dir_path.exists():
        continue

    print(f"\n【{dir_name}/】")

    # 直下のファイル数
    direct_py = len(list(dir_path.glob("*.py")))
    print(f"  直下のPyファイル: {direct_py}")

    # サブディレクトリ
    for subdir in sorted(dir_path.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith(".") and subdir.name != "__pycache__":
            sub_py = len(list(subdir.glob("*.py")))
            print(f"  ├─ {subdir.name}/: {sub_py} files")

# 問題点の分析
print()
print("=" * 80)
print("構造の問題点")
print("=" * 80)

issues = []

# scriptとscriptsの重複
if "script" in stats and "scripts" in stats:
    issues.append("⚠️  'script' と 'scripts' が両方存在（重複？）")

# 空または少ないディレクトリ
for dir_name, s in stats.items():
    if s["py"] == 0 and len(s["subdirs"]) == 0:
        issues.append(f"⚠️  '{dir_name}' は空または非Python")

# calc/plot の混在
for dir_name, s in stats.items():
    if s["calc"] > 0 and s["plot"] > 0:
        issues.append(f"ℹ️  '{dir_name}' にはcalcとplotが混在 (calc={s['calc']}, plot={s['plot']})")

for issue in issues:
    print(issue)
