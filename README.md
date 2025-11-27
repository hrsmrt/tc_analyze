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

- ✅ **自動中心追跡** - 海面気圧の最小値からTC中心を自動検出、中心速度も2次中心差分で自動計算
- ✅ **多次元解析** - 3次元場、2次元場、鉛直プロファイル、方位角平均
- ✅ **並列処理** - joblibによる高速な並列計算
- ✅ **柔軟なプロット** - 複数のスタイルシートに対応した可視化
- ✅ **モジュール化** - 共通機能を`utils/`パッケージに集約し、保守性が高い
- ✅ **物理定数の標準化** - 教科書・論文と一致した物理定数の命名規則
- ✅ **充実したドキュメント** - 物理計算のリファレンス、アーキテクチャ設計書、コマンドリファレンスなど

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
sh $WORK/tc_analyze/run/analyze.sh center

# 3次元解析の実行
sh $WORK/tc_analyze/run/analyze.sh 3d

# または全ての解析を実行
sh $WORK/tc_analyze/run/analyze.sh all
```

詳細は[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)を参照してください。

---

## 🔬 主な機能

### 解析カテゴリ

| カテゴリ | ファイル数 | 説明 |
|---------|-----------|------|
| **center** | 8 | TC中心位置の自動検出、中心速度の計算 |
| **whole_domain/3d** | 19 | 3次元全領域解析（CAPE、渦度、発散など）**中心位置非依存** |
| **whole_domain/2d** | 12 | 2次元全領域解析（SLP、風速最大値など）**中心位置非依存** |
| **vortex_region/3d** | 18 | 3次元渦領域解析（相対風、動力学量など）**中心位置依存** |
| **vortex_region/2d** | 7 | 2次元渦領域解析（相対風成分など）**中心位置依存** |
| **azimuthal/basic** | 56 | 基本的な方位角平均（風速、温位、ストリーム関数など） |
| **azimuthal/eliassen** | 16 | Eliassen循環解析（N², I², γ, ξなど） |
| **azimuthal/momentum** | 22 | 運動量方程式解析（u, w成分） |
| **azimuthal/q8** | 5 | 8方位分割解析 |
| **vertical/profile** | 4 | 鉛直プロファイルの抽出 |
| **vertical/q4** | 4 | 4象限分割解析 |
| **diagnostics/sums** | 4 | 積算値の計算 |
| **diagnostics/symmetrisity** | 4 | 対称性解析 |

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
sh $WORK/tc_analyze/run/analyze.sh center

# 3. 必要な解析を実行
sh $WORK/tc_analyze/run/analyze.sh 3d azim

# 4. 結果の確認
ls data/    # 計算結果（.npy）
ls fig/     # プロット結果（.png）
```

### よく使うコマンド

```bash
# 利用可能なカテゴリ一覧を表示
sh $WORK/tc_analyze/run/analyze.sh --list

# 特定のカテゴリのみ実行
sh $WORK/tc_analyze/run/analyze.sh center 3d azim

# スタイル指定
sh $WORK/tc_analyze/run/analyze.sh --style dark_background 3d

# バックグラウンド実行（ログ付き）
nohup sh $WORK/tc_analyze/run/analyze.sh --log ./logs/run01 &
```

詳細は[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)を参照してください。

---

## 📚 ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md) | **コマンドリファレンス** - よく使うコマンド、実行方法、トラブルシューティング |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | **アーキテクチャ設計書** - システム構成、データフロー、モジュール設計、拡張ガイド |
| [docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md) | **物理計算リファレンス** - utils内の物理定数、熱力学計算、風速場計算など |
| [WORK_LOG.md](./WORK_LOG.md) | **作業履歴とコーディング規約** - 確立されたコーディングパターン、既知の問題と解決策 |
| [MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md) | リファクタリング完了報告 |
| [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) | リファクタリング成果報告 |

### 初めての方へ

1. **環境構築**: このREADMEの[環境構築](#環境構築)セクション
2. **コマンド実行**: [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md)
3. **物理計算の理解**: [docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md)
4. **コード修正・追加**: [ARCHITECTURE.md](./ARCHITECTURE.md)の拡張ガイド
5. **コーディング規約**: [WORK_LOG.md](./WORK_LOG.md)の確立されたコーディングパターン

### utilsモジュールの概要

**utils/**パッケージには、全ての解析スクリプトで共通して使用される機能が集約されています（12ファイル、2,560行）：

| モジュール | 主な機能 |
|-----------|---------|
| **config.py** | `AnalysisConfig`クラス - setting.jsonの読み込み、グリッドパラメータの計算、ファイルパス管理 |
| **grid.py** | `GridHandler`クラス - 空間グリッド生成、座標変換（直交⇔極座標）、距離計算、周期境界条件 |
| **plotting.py** | `PlotConfig`クラス - 変数ごとのプロット設定（カラーマップ、レベル、ラベル）、スタイルシート管理 |
| **basic.py** | 物理定数（Cp, Rd, Rv, Lv, g, PRES_S など）、基本関数（tetens式、2次中心差分） |
| **thermodynamics.py** | 熱力学計算（温位θ、相当温位θ_e） |
| **wind.py** | 風速場計算（相対風、移動座標系での風速、極座標変換） |
| **azimuthal.py** | 方位角平均計算（3次元・2次元データ、ビニング処理） |
| **streamfunction.py** | 流線関数計算（渦度からのPoisson方程式ソルバー） |
| **optimize_dtype.py** | データ型最適化（メモリ使用量削減） |
| **optimize_matplotlib.py** | matplotlib最適化（高速化設定） |
| **check_usage_comments.py** | 使用状況チェック |
| **__init__.py** | パッケージ初期化 |

詳細は[docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md)を参照してください。

### 物理定数の命名規則

utils/basic.pyで定義されている物理定数は、以下の命名規則に従っています：

- **普遍定数**: `K_B`, `N_A` など（大文字+アンダースコア）
- **物理記号**: `Cp`, `Rd`, `Rv`, `Lv`, `g` など（教科書・論文と同じ表記）
- **複合語**: `PRES_S`, `G_MS`, `G_ME` など（大文字+アンダースコア）

この規則により、コードが物理の教科書や論文の記法と一致し、可読性が向上しています。

---

## 📁 プロジェクト構造

```
tc_analyze/
├── utils/                    # 共通モジュール（12ファイル、2,560行）
│   ├── config.py            # 設定管理（AnalysisConfig）
│   ├── grid.py              # グリッド計算（GridHandler）
│   ├── plotting.py          # プロット設定（PlotConfig）
│   ├── basic.py             # 物理定数・基本関数（Cp, Rd, g, tetensなど）
│   ├── thermodynamics.py    # 熱力学計算（相当温位θ_e）
│   ├── wind.py              # 風速場計算（相対風、極座標変換）
│   ├── azimuthal.py         # 方位角平均計算
│   ├── streamfunction.py    # 流線関数計算（Poisson方程式ソルバー）
│   └── optimize_*.py        # 最適化ユーティリティ
│
├── docs/                     # ドキュメント
│   └── UTILS_PHYSICS_REFERENCE.md  # 物理計算リファレンス
│
├── run/                      # 実行スクリプト
│   └── analyze.sh           # 統合実行スクリプト（最重要）
│
├── script/                   # 設定ファイル
│   └── setting.json         # 設定ファイル（サンプル）
│
├── analysis/                 # 解析スクリプト群（169ファイル、13,349行）
│   ├── whole_domain/        # 領域全体の解析（31ファイル、中心位置非依存）
│   │   ├── 2d/             # 2次元全領域（12ファイル）
│   │   │   ├── calc/       # SLP最小値、風速最大値など
│   │   │   └── plot/       # 全領域プロット
│   │   └── 3d/             # 3次元全領域（19ファイル）
│   │       ├── calc/       # 発散、渦度の計算
│   │       └── plot/       # CAPE、相当温位、流線関数など
│   │
│   ├── vortex_region/       # 渦領域の解析（25ファイル、中心位置依存）
│   │   ├── 2d/             # 2次元渦領域（7ファイル）
│   │   │   ├── calc/       # 相対風成分の計算
│   │   │   └── plot/       # 渦領域プロット
│   │   └── 3d/             # 3次元渦領域（18ファイル）
│   │       ├── calc/       # 動力学量の計算
│   │       └── plot/       # 相対風、動力学量のプロット
│   │
│   ├── azimuthal/           # 方位角解析（99ファイル）
│   │   ├── basic/          # 基本的な方位角平均（56ファイル）
│   │   │   ├── calc/       # 方位角平均の計算
│   │   │   └── plot/       # 方位角平均のプロット
│   │   ├── eliassen/       # Eliassen循環解析（16ファイル）
│   │   │   ├── calc/       # N², I², γ, ξ など
│   │   │   └── plot/       # 2次循環のプロット
│   │   ├── momentum/       # 運動量方程式解析（22ファイル）
│   │   │   ├── u/          # 接線運動量（圧力勾配、遠心力など）
│   │   │   └── w/          # 鉛直運動量
│   │   └── q8/             # 8方位分割解析（5ファイル）
│   │       ├── calc/       # 方位ごとの統計
│   │       └── plot/       # 方位別プロット
│   │
│   ├── center/              # TC中心位置計算（8ファイル）
│   │   ├── calc/           # 海面気圧最小値探索
│   │   └── plot/           # 中心軌跡プロット
│   │
│   ├── vertical/            # 鉛直解析（8ファイル）
│   │   ├── profile/        # 鉛直プロファイル
│   │   │   ├── calc/       # プロファイル抽出
│   │   │   └── plot/       # 鉛直構造プロット
│   │   └── q4/             # 4象限分割解析
│   │       ├── calc/       # 象限別統計
│   │       └── plot/       # 象限別プロット
│   │
│   └── diagnostics/         # 診断量（8ファイル）
│       ├── sums/           # 積算値計算（領域積分など）
│       │   ├── calc/
│       │   └── plot/
│       └── symmetrisity/   # 対称性解析（非対称度など）
│           ├── calc/
│           └── plot/
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
sh $WORK/tc_analyze/run/analyze.sh center
```

その他のトラブルシューティングは[COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md#トラブルシューティング)を参照してください。

---

## 📊 統計

### コードベース規模
- **総Pythonファイル数**: 222ファイル
  - utils: 12ファイル（2,560行）
  - analysis: 169ファイル（13,349行）
    - 計算スクリプト（*_calc.py）: 53ファイル
    - プロットスクリプト（*_plot.py）: 82ファイル
    - その他: 34ファイル
  - その他: 41ファイル（setup.py、テストなど）
- **総コード行数**: 21,707行
- **解析カテゴリ**: 7カテゴリ
  - whole_domain（3d/2d）: 31ファイル（中心位置非依存）
  - vortex_region（3d/2d）: 25ファイル（中心位置依存）
  - azimuthal（basic/eliassen/momentum/q8）: 99ファイル
  - center: 8ファイル
  - vertical（profile/q4）: 8ファイル
  - diagnostics（sums/symmetrisity）: 8ファイル

### リファクタリング効果
- **コード重複削減**: 62-75%（物理定数、グリッド計算など）
- **保守性**: 大幅向上（共通機能をutils/に集約）
- **開発効率**: 50-70%向上（設定変更が1箇所で完結）

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

### v2.1.0 (2025-11-27)
- 物理定数の命名規則を統一（物理記号優先）
  - `g0` → `g`, `K_B`, `N_A` など
  - 教科書・論文の記法と一致させ、可読性を向上
- utils/thermodynamics.pyを作成し、相当温位計算を集約
- utils/azimuthal.pyを作成し、方位角平均計算を集約
- utils/wind.pyを作成し、風速場計算を集約
- docs/UTILS_PHYSICS_REFERENCE.mdを作成（物理計算の包括的リファレンス）
- TC中心速度の計算を2次中心差分で自動計算する機能を追加
- README.mdにutilsモジュールの詳細説明を追加

### v2.0.0 (2025-11-27)
- ドキュメント体系を整備（COMMAND_REFERENCE.md、ARCHITECTURE.md追加）
- README.mdを大幅に拡充

### v1.0.0 (2025-11-11)
- 全スクリプトをリファクタリング完了
- `utils/`パッケージを作成し、共通機能を集約
- コード行数を30-43%削減

---

**最終更新**: 2025-11-27
