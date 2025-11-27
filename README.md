# tc_analyze

**熱帯低気圧（TC）の3次元直交座標データ解析ツール**

修士課程の研究で使用している、NICAM出力データを解析するためのPythonコード群です。

---

## 📋 目次

- [概要](#概要)
- [クイックスタート](#クイックスタート)
- [主な機能](#主な機能)
- [環境構築](#環境構築)
- [使い方](#使い方)
- [ドキュメント](#ドキュメント)
- [プロジェクト構造](#プロジェクト構造)
- [ライセンス](#ライセンス)

---

## 🎯 概要

このプロジェクトは、熱帯低気圧（TC）のシミュレーションデータを多角的に解析するためのツール群です。

### 主な特徴

- ✅ **自動中心追跡** - 海面気圧の最小値からTC中心を自動検出
- ✅ **多次元解析** - 3次元場、2次元場、鉛直プロファイル、方位角平均
- ✅ **並列処理** - joblibによる高速な並列計算
- ✅ **柔軟なプロット** - 複数のスタイルシートに対応した可視化
- ✅ **モジュール化** - 共通機能を`utils/`パッケージに集約し、保守性が高い

### 技術スタック

- **Python** >= 3.8
- **NumPy** - 数値計算
- **Matplotlib** - 可視化
- **Joblib** - 並列処理

---

## 🚀 クイックスタート

### 1. インストール

```bash
# プロジェクトルートに移動
cd /path/to/tc_analyze

# 開発モードでインストール（utilsパッケージを使えるようにする）
pip install -e .
```

### 2. 設定ファイルの準備

作業ディレクトリに`setting.json`を配置します（サンプル: `script/setting.json`）。

```json
{
  "nt": 101,
  "glevel": 7,
  "triangle_size": 256000.0,
  "dt_output": 86400,
  "input_folder": "../convert/",
  "vgrid_filepath": "/path/to/vgrid_c74.txt",
  "n_jobs": 4
}
```

### 3. 解析の実行

```bash
# 作業ディレクトリに移動（setting.jsonがある場所）
cd /path/to/workdir

# TC中心位置の計算（最初に必要）
sh $WORK/tc_analyze/script/analyze.sh center

# 3次元解析の実行
sh $WORK/tc_analyze/script/analyze.sh 3d

# または全ての解析を実行
sh $WORK/tc_analyze/script/analyze.sh all
```

詳細は[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)を参照してください。

---

## 🔬 主な機能

### 解析カテゴリ

| カテゴリ | 説明 |
|---------|------|
| **center** | TC中心位置の自動検出 |
| **3d** | 3次元場の解析（発散、渦度、風速場など） |
| **2d** | 2次元場の解析（全領域・渦領域） |
| **z_profile** | 鉛直プロファイルの抽出 |
| **azim** | 方位角平均解析（基本） |
| **azim_eliassen** | Eliassen方程式関連 |
| **azim_eq_momentum_u** | 運動量方程式（u成分） |
| **azim_q8** | 8方位分割解析 |
| **sums** | 積算値の計算 |
| **symmetrisity** | 対称性解析 |

### データフロー

システムには2つのデータフローパターンが存在します：

#### パターン1: 2段階処理
```
入力データ (.grd)
    ↓
計算スクリプト (*_calc.py)
    ↓
中間データ (.npy)
    ↓
プロットスクリプト (*_plot.py)
    ↓
出力図 (.png)
```
例: 方位角平均、発散・渦度計算など

#### パターン2: 直接プロット
```
入力データ (.grd)
    ↓
プロットスクリプト (*_plot.py)
    ↓
出力図 (.png)
```
例: 2d/whole_domain.py など

詳細は[ARCHITECTURE.md](./ARCHITECTURE.md)を参照してください。

---

## 🔧 環境構築

### 必要なソフトウェア

- Python >= 3.8
- pip

### 依存パッケージ

`setup.py`で自動的にインストールされます：

- numpy
- matplotlib
- joblib

### インストール手順

```bash
# 1. リポジトリのクローン（または入手）
cd /path/to/your/workspace

# 2. tc_analyzeディレクトリに移動
cd tc_analyze

# 3. 開発モードでインストール
pip install -e .

# 4. インストール確認
python -c "from utils.config import AnalysisConfig; print('OK')"
```

### 環境変数の設定（オプション）

```bash
# .bashrc または .zshrc に追加
export WORK=/path/to/your/workspace
export MPLSTYLE=dark_background  # プロットスタイルを一括指定
```

---

## 💻 使い方

### 基本的な実行フロー

```bash
# 1. 作業ディレクトリに移動（setting.jsonがある場所）
cd /path/to/workdir

# 2. 中心位置の計算（最初に実行が必要）
sh $WORK/tc_analyze/script/analyze.sh center

# 3. 必要な解析を実行
sh $WORK/tc_analyze/script/analyze.sh 3d azim

# 4. 結果の確認
ls data/    # 計算結果（.npy）
ls fig/     # プロット結果（.png）
```

### よく使うコマンド

```bash
# 利用可能なカテゴリ一覧を表示
sh $WORK/tc_analyze/script/analyze.sh --list

# 特定のカテゴリのみ実行
sh $WORK/tc_analyze/script/analyze.sh center 3d azim

# スタイル指定
sh $WORK/tc_analyze/script/analyze.sh --style dark_background 3d

# バックグラウンド実行（ログ付き）
nohup sh $WORK/tc_analyze/script/analyze.sh --log ./logs/run01 &
```

詳細は[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)を参照してください。

---

## 📚 ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md) | **コマンドリファレンス** - よく使うコマンド、実行方法、トラブルシューティング |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | **アーキテクチャ設計書** - システム構成、データフロー、モジュール設計、拡張ガイド |
| [WORK_LOG.md](./WORK_LOG.md) | **作業履歴とコーディング規約** - 確立されたコーディングパターン、既知の問題と解決策 |
| [MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md) | リファクタリング完了報告 |
| [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) | リファクタリング成果報告 |

### 初めての方へ

1. **環境構築**: このREADMEの[環境構築](#環境構築)セクション
2. **コマンド実行**: [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)
3. **コード修正・追加**: [ARCHITECTURE.md](./ARCHITECTURE.md)の拡張ガイド
4. **コーディング規約**: [WORK_LOG.md](./WORK_LOG.md)の確立されたコーディングパターン

---

## 📁 プロジェクト構造

```
tc_analyze/
├── utils/                    # 共通モジュール（重要）
│   ├── config.py            # 設定管理
│   ├── grid.py              # グリッド計算
│   ├── plotting.py          # プロット設定
│   └── basic.py             # 物理定数
│
├── script/                   # 実行スクリプト
│   ├── analyze.sh           # 統合実行スクリプト（最重要）
│   └── setting.json         # 設定ファイル（サンプル）
│
├── 3d/                       # 3次元解析スクリプト
├── 2d/                       # 2次元解析スクリプト
├── azim_mean/                # 方位角平均解析スクリプト
├── center/                   # TC中心位置計算
├── z_profile/                # 鉛直プロファイル
├── ... その他多数 ...
│
├── setup.py                  # パッケージ設定
├── README.md                 # このファイル
├── COMMAND_REFERENCE.md      # コマンドリファレンス
├── ARCHITECTURE.md           # アーキテクチャ設計書
├── WORK_LOG.md               # 作業履歴・コーディング規約
└── CLAUDE.md                 # AI支援用コンテキスト
```

詳細は[ARCHITECTURE.md](./ARCHITECTURE.md)を参照してください。

---

## 🔍 トラブルシューティング

### よくあるエラーと解決策

#### `ModuleNotFoundError: No module named 'utils'`

```bash
cd /path/to/tc_analyze
pip install -e .
```

#### `FileNotFoundError: setting.json not found`

```bash
# setting.jsonがあるディレクトリで実行
cd /path/to/workdir
ls setting.json  # 確認
```

#### `FileNotFoundError: ss_slp_center_x.txt not found`

```bash
# centerカテゴリを最初に実行
sh $WORK/tc_analyze/script/analyze.sh center
```

その他のトラブルシューティングは[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md#トラブルシューティング)を参照してください。

---

## 📊 統計

- **総スクリプト数**: 180+
  - 計算スクリプト: 60+
  - プロットスクリプト: 83+
- **解析カテゴリ**: 12+
- **総コード行数**: 約8,000-10,000行（リファクタリング後）
- **コード削減率**: 30-43%（リファクタリングにより）

---

## 🤝 貢献

このプロジェクトは修士研究の一環として開発されています。

改善提案や問題報告は、開発者に直接連絡してください。

---

## 📝 ライセンス

研究用途。詳細は開発者に確認してください。

---

## 👤 開発者

修士課程学生

---

## 📅 更新履歴

### v2.0.0 (2025-11-27)
- ドキュメント体系を整備（COMMAND_REFERENCE.md、ARCHITECTURE.md追加）
- README.mdを大幅に拡充

### v1.0.0 (2025-11-11)
- 全スクリプトをリファクタリング完了
- `utils/`パッケージを作成し、共通機能を集約
- コード行数を30-43%削減

---

**最終更新**: 2025-11-27
