# コマンドリファレンス

## 📋 目次
- [環境セットアップ](#環境セットアップ)
- [よく使うコマンド](#よく使うコマンド)
- [CLIツール（tc-analyze）](#cliツールtc-analyze)
- [解析実行](#解析実行)
- [カテゴリ一覧](#カテゴリ一覧)
- [トラブルシューティング](#トラブルシューティング)

---

## 🔧 環境セットアップ

### 初回セットアップ

```bash
# 1. プロジェクトルートに移動
cd /path/to/tc_analyze

# 2. 開発モードでインストール（utilsパッケージを使えるようにする）
pip install -e .

# 3. 設定ファイルを確認
ls -l script/setting.json
```

### 必要なパッケージ

```bash
# requirements（自動でインストールされる）
numpy
matplotlib
joblib

# Python バージョン
python >= 3.8
```

### ディレクトリ構成の確認

```bash
# データと図の出力先が作成されているか確認
ls -ld data/ fig/

# なければ自動で作成される（スクリプト実行時）
```

---

## ⚡ よく使うコマンド

### 基本コマンド

```bash
# 【最重要】全ての解析を実行
cd /path/to/workdir  # setting.jsonがあるディレクトリ
sh $WORK/tc_analyze/run/analyze.sh

# 特定カテゴリのみ実行
sh $WORK/tc_analyze/run/analyze.sh center 3d azim

# 利用可能なカテゴリ一覧を表示
sh $WORK/tc_analyze/run/analyze.sh --list

# ドライラン（実行せずにコマンドを確認）
sh $WORK/tc_analyze/run/analyze.sh --dry-run center 3d
```

### スタイル指定

```bash
# 暗い背景でプロット
sh $WORK/tc_analyze/run/analyze.sh --style dark_background

# 環境変数で一括指定（推奨）
export MPLSTYLE=dark_background
sh $WORK/tc_analyze/run/analyze.sh

# カスタムスタイルファイル
sh $WORK/tc_analyze/run/analyze.sh --style /path/to/custom.mplstyle
```

### バックグラウンド実行

```bash
# ログファイルを出力してバックグラウンド実行
nohup sh $WORK/tc_analyze/run/analyze.sh --log ./logs/run01 &

# プロセス確認
jobs
ps aux | grep analyze.sh

# ログ確認
tail -f ./logs/run01_stdout.log
tail -f ./logs/run01_stderr.log
```

### 並列実行の制御

```bash
# setting.json で並列数を設定
{
  "n_jobs": 4,  # 4並列で実行
  ...
}

# または環境変数で制御（開発中）
```

---

## 🛠️ CLIツール（tc-analyze）

`tc-analyze`コマンドは、データ管理、設定確認、可視化を簡単に行うためのコマンドラインインターフェースです。

### インストール

```bash
# プロジェクトルートで開発モードでインストール
cd /path/to/tc_analyze
pip install -e .

# インストール確認
tc-analyze --help
```

### データ管理コマンド

#### データファイル一覧表示

```bash
# 全てのデータファイルをリスト表示
tc-analyze data list --config run/setting.json

# 特定タイプのみ表示
tc-analyze data list --type center --config run/setting.json
tc-analyze data list --type azim --config run/setting.json
```

#### データファイル情報表示

```bash
# ファイルの詳細情報を表示（形状、データ型、メタデータ）
tc-analyze data info center/ss_slp/center.npz --config run/setting.json
tc-analyze data info azim/azim_wind_radial/t000.npy --config run/setting.json

# .npz/.npyどちらも対応
tc-analyze data info center/ms_pres/center.npz
```

#### データ統計表示

```bash
# データの統計情報を表示（最小値、最大値、平均、標準偏差）
tc-analyze data stats center/ss_slp/center.npz --config run/setting.json
```

#### メタデータの編集（.npzファイル）

```bash
# 対話的にメタデータを追加・編集・削除
tc-analyze data annotate center/ss_slp/center.npz --config run/setting.json

# 絶対パスでも可
tc-analyze data annotate /path/to/data/center.npz
```

**対話メニュー:**
- `[a]` Add - 新しいメタデータを追加（description, notes, authorなど）
- `[e]` Edit - 既存のメタデータを編集
- `[d]` Delete - メタデータを削除
- `[s]` Save - 変更を保存（自動バックアップ作成）
- `[q]` Quit - 保存せずに終了

**使用例:**
```
Choose an option: a
Enter key name: description
Value type: string
Enter value: SS SLP center with r_refine=100km, calculated on 2025-11-28

Choose an option: s
Save changes? [y/N]: y
✓ Saved changes to center.npz
```

### 設定管理コマンド

#### 設定情報の表示

```bash
# 設定ファイルの内容を整形表示
tc-analyze config show --config run/setting.json

# 全てのパラメータを確認
tc-analyze config show | less
```

#### 設定ファイルの検証

```bash
# 設定ファイルの妥当性を検証
tc-analyze config validate --config run/setting.json
```

### 中心座標コマンド

#### 中心座標のメタデータ確認

```bash
# SS SLP中心座標の詳細情報を表示
tc-analyze center inspect ss_slp --config run/setting.json

# MS PRES中心座標の詳細情報を表示
tc-analyze center inspect ms_pres --config run/setting.json

# 詳細モード（全メタデータを表示）
tc-analyze center inspect ss_slp --verbose --config run/setting.json
```

**出力例:**
```
🔍 Inspecting ss_slp center coordinates

  File: data/center/ss_slp/center.npz
  Format: .npz

📍 Center Coordinates:
  Shape: (145, 2)
  Type: 2D center (nt=145)
  X range: [1200.50, 1350.75] km
  Y range: [1100.25, 1250.80] km

📊 Metadata:
  r_refine                      : 100000 m (100.0 km)
  actual_iterations             : mean=5.23, max=15
  max_iterations                : 100

✓ Inspection complete
```

#### 中心軌道のプロット

```bash
# SS SLP中心の軌道をプロット
tc-analyze center plot --method ss_slp --config run/setting.json

# MS PRES中心の軌道をプロット（z=10）
tc-analyze center plot --method ms_pres --z-level 10 --config run/setting.json

# グリッド線を表示
tc-analyze center plot --method ss_slp --grid --config run/setting.json

# 出力先を指定
tc-analyze center plot --method ss_slp --output ./custom_path.png
```

### ヘルプの表示

```bash
# メインヘルプ
tc-analyze --help

# サブコマンドのヘルプ
tc-analyze data --help
tc-analyze config --help
tc-analyze center --help

# 特定コマンドのヘルプ
tc-analyze data list --help
tc-analyze center plot --help
```

### 設定ファイルの指定方法

```bash
# --config オプションで指定
tc-analyze data list --config run/setting.json

# カレントディレクトリのsetting.jsonを使用
cd /path/to/workdir
tc-analyze data list

# 相対パスでも可
tc-analyze data list --config ../other_dir/setting.json
```

### 中心座標の管理

詳細な中心座標の設定と管理については、[CENTER_CONFIGURATION.md](./CENTER_CONFIGURATION.md)を参照してください。

**主な機能:**
- パラメータの異なる複数の中心座標を管理
- setting.jsonで使用する中心座標ファイルを切り替え
- 計算パラメータの確認と編集
- メタデータの追加と管理

---

## 📊 解析実行

### 標準的な実行フロー

```bash
# 1. 作業ディレクトリに移動（setting.jsonがある場所）
cd /path/to/your/workdir

# 2. 設定ファイルの確認
cat setting.json

# 3. 中心位置の計算（最初に実行が必要）
sh $WORK/tc_analyze/run/analyze.sh center

# 4. 3次元解析
sh $WORK/tc_analyze/run/analyze.sh 3d

# 5. 方位角平均解析
sh $WORK/tc_analyze/run/analyze.sh azim

# 6. 全て実行
sh $WORK/tc_analyze/run/analyze.sh all
```

### カテゴリごとの実行

```bash
# 【重要】centerは最初に実行する必要がある
# （中心位置データが他の解析で使われるため）
sh $WORK/tc_analyze/run/analyze.sh center

# 3次元解析（全領域・渦領域）
sh $WORK/tc_analyze/run/analyze.sh 3d

# 2次元解析
sh $WORK/tc_analyze/run/analyze.sh 2d

# 鉛直プロファイル
sh $WORK/tc_analyze/run/analyze.sh z_profile

# 渦領域解析（3d, 2d, z_profileの渦領域のみ）
sh $WORK/tc_analyze/run/analyze.sh vortex_region

# 方位角平均解析（基本）
sh $WORK/tc_analyze/run/analyze.sh azim

# 方位角平均解析（Eliassen方程式関連）
sh $WORK/tc_analyze/run/analyze.sh azim_eliassen

# 方位角平均解析（運動量方程式 u成分）
sh $WORK/tc_analyze/run/analyze.sh azim_eq_momentum_u

# 方位角平均解析（運動量方程式 w成分）
sh $WORK/tc_analyze/run/analyze.sh azim_eq_momentum_w

# 方位角平均解析（8方位分割）
sh $WORK/tc_analyze/run/analyze.sh azim_q8

# 合計値の計算
sh $WORK/tc_analyze/run/analyze.sh sums

# 対称性解析
sh $WORK/tc_analyze/run/analyze.sh symmetrisity

# 鉛直プロファイル（4象限）
sh $WORK/tc_analyze/run/analyze.sh z_profile_q4
```

### 複数カテゴリの組み合わせ

```bash
# 中心位置と3次元解析のみ
sh $WORK/tc_analyze/run/analyze.sh center 3d

# 方位角平均系を全て実行
sh $WORK/tc_analyze/run/analyze.sh azim azim_eliassen azim_eq_momentum_u azim_q8
```

---

## 📁 カテゴリ一覧

### 基本カテゴリ

| カテゴリ | 説明 | 依存関係 | 出力先 |
|---------|------|---------|--------|
| `center` | **TC中心位置の計算** | なし（最初に実行） | `data/ss_slp_center_*.txt` |
| `3d` | 3次元場の解析（全領域） | center | `data/3d/`, `fig/3d/whole_domain/` |
| `2d` | 2次元場の解析 | center | `data/2d/`, `fig/2d/` |
| `z_profile` | 鉛直プロファイル | center | `data/z_profile/`, `fig/z_profile/` |

### 渦領域解析

| カテゴリ | 説明 | 依存関係 | 出力先 |
|---------|------|---------|--------|
| `vortex_region` | 3d, 2d, z_profileの渦領域のみ実行 | center, 各種calcスクリプト | `fig/3d/vortex_region/` など |

### 方位角平均解析

| カテゴリ | 説明 | 依存関係 | 出力先 |
|---------|------|---------|--------|
| `azim` | 基本的な方位角平均 | center | `data/azim/`, `fig/azim/` |
| `azim_eliassen` | Eliassen方程式関連 | center, azim | `data/azim/eliassen/`, `fig/azim/eliassen/` |
| `azim_eq_momentum_u` | 運動量方程式（u成分） | center, azim | `data/azim/eq_momentum_u/`, `fig/azim/eq_momentum_u/` |
| `azim_eq_momentum_w` | 運動量方程式（w成分） | center, azim | `data/azim/eq_momentum_w/`, `fig/azim/eq_momentum_w/` |
| `azim_q8` | 8方位分割解析 | center | `data/azim_q8/`, `fig/azim_q8/` |

### その他

| カテゴリ | 説明 | 依存関係 | 出力先 |
|---------|------|---------|--------|
| `sums` | 積算値の計算とプロット | 3d, azim | `data/sums/`, `fig/sums/` |
| `symmetrisity` | 対称性の解析 | center, azim | `data/symmetrisity/`, `fig/symmetrisity/` |
| `z_profile_q4` | 鉛直プロファイル（4象限分割） | center | `data/z_profile_q4/`, `fig/z_profile_q4/` |
| `all` | 全カテゴリを実行 | - | 全て |

---

## 🔍 トラブルシューティング

### よくあるエラー

#### 1. `ModuleNotFoundError: No module named 'utils'`

**原因**: `pip install -e .` が実行されていない

**解決策**:
```bash
cd /path/to/tc_analyze
pip install -e .
```

#### 2. `FileNotFoundError: setting.json not found`

**原因**: setting.jsonがないディレクトリで実行している

**解決策**:
```bash
# setting.jsonがあるディレクトリに移動
cd /path/to/workdir
ls setting.json  # 確認

# スクリプトを実行
sh $WORK/tc_analyze/run/analyze.sh
```

#### 3. `FileNotFoundError: ss_slp_center_x.txt not found`

**原因**: centerカテゴリが実行されていない

**解決策**:
```bash
# 最初にcenterを実行
sh $WORK/tc_analyze/run/analyze.sh center

# その後、他のカテゴリを実行
sh $WORK/tc_analyze/run/analyze.sh 3d
```

#### 4. データサイズの不一致エラー

**原因**: 古いビニング方法で作成されたデータ

**解決策**:
```bash
# 該当する*_calc.pyスクリプトを再実行
cd /path/to/tc_analyze/azim_mean
python azim_wind_calc.py

# または該当カテゴリを再実行
sh $WORK/tc_analyze/run/analyze.sh azim
```

#### 5. プロット時のTypeError: Shapes do not match

**原因**: グリッドサイズとデータサイズの不一致

**解決策**: WORK_LOG.mdの「確立されたコーディングパターン」を参照して修正

### デバッグ方法

```bash
# 詳細な出力を表示
sh $WORK/tc_analyze/run/analyze.sh --verbose center

# 実行せずにコマンドを確認
sh $WORK/tc_analyze/run/analyze.sh --dry-run 3d

# エラーで停止する（デフォルトは継続）
sh $WORK/tc_analyze/run/analyze.sh --stop-on-error 3d

# 個別にスクリプトを実行してデバッグ
cd /path/to/tc_analyze/3d
python divergence_calc.py
```

### ログの確認

```bash
# バックグラウンド実行時のログ
tail -f ./logs/run01_stdout.log  # 標準出力
tail -f ./logs/run01_stderr.log  # エラー出力

# ログファイルから特定のエラーを検索
grep -i error ./logs/run01_stderr.log
grep -i "traceback" ./logs/run01_stderr.log
```

---

## 🎯 ベストプラクティス

### 推奨される実行順序

```bash
# 1. 環境セットアップ（初回のみ）
cd /path/to/tc_analyze
pip install -e .

# 2. 作業ディレクトリに移動
cd /path/to/workdir

# 3. 設定ファイルの確認・編集
vi setting.json

# 4. 中心位置の計算（必須）
sh $WORK/tc_analyze/run/analyze.sh center

# 5. 必要な解析を実行
sh $WORK/tc_analyze/run/analyze.sh 3d azim

# または全て実行
sh $WORK/tc_analyze/run/analyze.sh all
```

### 大規模解析の場合

```bash
# スタイルを環境変数で設定
export MPLSTYLE=dark_background

# 並列数をsetting.jsonで設定
# { "n_jobs": 8, ... }

# ログ付きでバックグラウンド実行
nohup sh $WORK/tc_analyze/run/analyze.sh --log ./logs/main &

# 進捗確認
tail -f ./logs/main_stdout.log
```

### データの再計算

```bash
# 計算のみ再実行（プロットはスキップ）
cd /path/to/tc_analyze/azim_mean
python azim_wind_calc.py

# プロットのみ再実行
python azim_wind_radial_plot.py

# カテゴリ全体を再実行
sh $WORK/tc_analyze/run/analyze.sh azim
```

---

## 📚 関連ドキュメント

- [README.md](../README.md) - プロジェクト概要
- [ARCHITECTURE.md](./ARCHITECTURE.md) - アーキテクチャ設計
- [CENTER_CONFIGURATION.md](./CENTER_CONFIGURATION.md) - 中心座標設定ガイド
- [UTILS_PHYSICS_REFERENCE.md](./UTILS_PHYSICS_REFERENCE.md) - 物理計算リファレンス
- [WORK_LOG.md](../WORK_LOG.md) - コーディングパターンと作業履歴
- [MIGRATION_COMPLETE.md](../MIGRATION_COMPLETE.md) - リファクタリング完了報告

---

**最終更新日**: 2025-11-28
**バージョン**: 1.1
