# TC解析プロジェクトのコンテキスト

このプロジェクトは修士課程の研究で使用している熱帯低気圧の解析コード群です。

**プロジェクト規模**: 222ファイル、21,707行（Python）

---

## 📚 主要ドキュメント

### 必須ドキュメント（優先度順）

1. **プロジェクト概要**
   @./README.md
   - 全体像、環境構築、クイックスタート

2. **解析ワークフロー（NEW! 2025-11-28）**
   @./ANALYSIS_WORKFLOW.md
   - 解析の実行順序、依存関係の整理
   - 並列実行可能な処理の明確化
   - 中心非依存 vs 中心依存解析

3. **コマンドリファレンス（よく使うコマンド）**
   @./docs/COMMAND_REFERENCE.md
   - analyze.shの使い方、トラブルシューティング

4. **アーキテクチャ設計書**
   @./docs/ARCHITECTURE.md
   - システム構成、データフロー、拡張ガイド

5. **物理計算リファレンス（2025-11-27）**
   @./docs/UTILS_PHYSICS_REFERENCE.md
   - utils内の全物理定数（Cp, Rd, g, PRES_Sなど）
   - 熱力学計算（温位θ、相当温位θ_e）
   - 風速場計算、方位角平均、流線関数など

6. **作業履歴とコーディング規約**
   @./WORK_LOG.md
   - 確立されたコーディングパターン
   - グリッド生成、ビニング方法の統一
   - ディレクトリ構造とパス生成

### 補足ドキュメント

7. **リファクタリング概要**
   @./archive/docs/REFACTORING_SUMMARY.md

8. **マイグレーション完了報告**
   @./archive/docs/MIGRATION_COMPLETE.md

---

## ⚡ クイックリファレンス

### 環境セットアップ
```bash
cd /path/to/tc_analyze
pip install -e .
```

### よく使うコマンド
```bash
# 全解析実行
sh $WORK/tc_analyze/run/analyze.sh all

# 特定カテゴリのみ
sh $WORK/tc_analyze/run/analyze.sh center 3d azim

# カテゴリ一覧表示
sh $WORK/tc_analyze/run/analyze.sh --list
```

### utilsモジュール（15ファイル、2,900+行）
```python
from utils.config import AnalysisConfig      # 設定管理（中心座標読み込み含む）
from utils.grid import GridHandler           # グリッド計算
from utils.plotting import PlotConfig        # プロット設定
from utils.center import find_pressure_center  # 低気圧中心検出
from utils.basic import Cp, Rd, Rv, Lv, g   # 物理定数
from utils.thermodynamics import calculate_theta_e  # 相当温位
from utils.wind import calculate_relative_wind      # 相対風
from utils.azimuthal import calculate_azimuthal_mean_3d  # 方位角平均
from utils.streamfunction import solve_poisson_jacobi    # 流線関数
from utils.vorticity import calculate_vorticity_z        # 渦度計算（NEW! 2025-11-28）
from utils.metadata import read_data_metadata, get_data_statistics  # メタデータ読み込み
```

### CLIツール（`tc-analyze`コマンド）
```bash
# データ管理
tc-analyze data list --config run/setting.json
tc-analyze data info center/ss_slp/center.npz --config run/setting.json
tc-analyze data stats center/ss_slp/center.npz --config run/setting.json

# 設定管理
tc-analyze config show --config run/setting.json
tc-analyze config validate --config run/setting.json

# 可視化
tc-analyze center plot --method ss_slp --config run/setting.json
tc-analyze center plot --method ms_pres --z-level 10 --config run/setting.json
```

### 新しいパスメソッド（2025-11-28導入）
データ/図の出力パスを3つのカテゴリに明確に分類：
```python
from utils.config import AnalysisConfig
config = AnalysisConfig()

# 1. 中心非依存データ（全領域解析、領域平均）
path = config.get_domain_path("whole_domain", "3d/vorticity_z")
path = config.get_domain_path("vertical", "profile")

# 2. 中心座標データ
path = config.get_center_path("ss_slp")
path = config.get_center_path("ms_pres")

# 3. TC相対座標系データ（中心依存）
path = config.get_tc_centric_path("azimuthal", "basic/wind")
path = config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_radial")  # 相対風
path = config.get_tc_centric_path("vertical", "q4/zeta")
path = config.get_tc_centric_path("diagnostics", "symmetrisity")

# data_type="fig" で図の出力パス
path = config.get_domain_path("whole_domain", "2d/slp", data_type="fig")
```

### 物理定数の命名規則（2025-11-27統一）
- **普遍定数**: `K_B`, `N_A` (大文字+アンダースコア)
- **物理記号**: `Cp`, `Rd`, `Rv`, `Lv`, `g` (教科書表記)
- **複合語**: `PRES_S`, `G_MS`, `G_ME` (大文字+アンダースコア)

### ディレクトリ構成
```
tc_analyze/
├── utils/          # 共通モジュール（15ファイル、2,900+行）
│   ├── config.py, grid.py, plotting.py  # コア機能
│   ├── center.py                        # 中心検出アルゴリズム
│   ├── basic.py, thermodynamics.py      # 物理定数・計算
│   ├── wind.py, azimuthal.py            # 風速・方位角平均
│   ├── streamfunction.py                # 流線関数
│   ├── vorticity.py                     # 渦度計算（NEW! 2025-11-28）
│   └── metadata.py                      # メタデータ読み込み（.npz/.npy）
├── tc_analyze/     # CLIツール（6ファイル）
│   ├── cli.py                           # メインCLIアプリケーション
│   └── commands/                        # サブコマンド
│       ├── data.py                      # データ管理（list, info, stats）
│       ├── config_cmd.py                # 設定管理（show, validate）
│       └── center.py                    # 中心解析（plot）
├── analysis/       # 解析スクリプト（170ファイル、13,484行）
│   ├── whole_domain/  # 領域全体（旧構造、2025-11-28に再編成）
│   ├── vortex_region/ # 渦領域（旧構造、2025-11-28に再編成）
│   ├── center/        # TC中心位置計算（9: ss_slp, ms_pres）
│   ├── azimuthal/     # 方位角解析（旧構造、2025-11-28に再編成）
│   ├── vertical/      # 鉛直解析（旧構造、2025-11-28に再編成）
│   └── diagnostics/   # 診断解析（旧構造、2025-11-28に再編成）
├── data/           # データ出力（2025-11-28に3カテゴリに再編成）
│   ├── domain/        # 中心非依存データ（全領域解析、鉛直プロファイル）
│   ├── center/        # 中心座標データ（ss_slp, ms_pres）
│   └── tc_centric/    # TC相対座標系データ（方位角平均、渦領域等）
├── fig/            # 図出力（2025-11-28に3カテゴリに再編成）
│   ├── domain/        # 中心非依存データの図
│   ├── center/        # 中心座標データの図
│   └── tc_centric/    # TC相対座標系データの図
├── docs/           # ドキュメント
│   ├── COMMAND_REFERENCE.md, ARCHITECTURE.md
│   ├── WORK_LOG.md  # 作業履歴とコーディング規約
│   ├── UTILS_PHYSICS_REFERENCE.md  # 物理計算リファレンス
│   └── DIRECTORY_REORGANIZATION_COMPLETE.md  # ディレクトリ再編成完了報告
├── run/            # 実行スクリプト（analyze.sh）
├── script/         # 設定ファイル（setting.json）
└── archive/        # アーカイブ
```

---

## 📋 重要な注意事項

### コーディング規約
- **コードスタイル**: pylint, autoflake, isort, autopep8 で整形済み
- **物理定数**: `utils.basic`から必ずインポート（Cp, Rd, Rv, Lv, g, PRES_S）
- **グリッド計算**: `GridHandler`を使用（直接計算しない）
- **方位角平均**: `utils.azimuthal`の関数を使用（ビニング方法統一済み）
- **渦度計算**: `utils.vorticity.calculate_vorticity_z()`を使用（重複コード削減）
- **パス生成**: 新しいパスメソッドを使用（`get_domain_path`, `get_center_path`, `get_tc_centric_path`）
- **設定管理**: `AnalysisConfig`を使用（setting.json直接読み込み禁止）
- **中心座標**: `config.center_x`, `config.center_y`を使用（2d: nt, 3d: nt×nz）
- **中心検出**: `utils.center.find_pressure_center()`を使用（アルゴリズム統一済み）

### システム構成
- **設定ファイル**: `script/setting.json` または作業ディレクトリの`setting.json`
- **実行スクリプト**: `run/analyze.sh` でカテゴリ別に実行
- **Python環境**: `pip install -e .` で開発モードインストール必須
- **依存関係**: numpy, matplotlib, joblib（setup.pyで自動インストール）
- **ディレクトリ構造**: 解析タイプ別 + calc/plot分離

### 最近の主要変更

#### 2025-11-28
- ✅ **ディレクトリ再編成の完了**（全170ファイルマイグレーション）
  - **3つのカテゴリへの明確な分類**: data/とfig/を3カテゴリに整理
    - `domain/` - 中心非依存データ（全領域解析、鉛直プロファイル）
    - `center/` - 中心座標データ（ss_slp, ms_pres）
    - `tc_centric/` - TC相対座標系データ（方位角平均、渦領域、診断解析）
  - **新しいパスメソッドの追加** (`utils/config.py`)
    - `get_domain_path()` - 中心非依存データのパス生成
    - `get_center_path()` - 中心座標データのパス生成
    - `get_tc_centric_path()` - TC相対座標系データのパス生成
  - **渦度計算の共通化** (`utils/vorticity.py`新規作成)
    - `calculate_vorticity_z()` - z方向渦度計算
    - 重複コード52行削減、オンデマンド計算でストレージ節約
  - **流線関数プロットのオンデマンド化**
    - u/v → 渦度 → 流線関数を全て実行時計算
    - 数GB〜数百GBのストレージ節約
  - **相対風の正しい分類**
    - TC移動速度に依存する相対風を`tc_centric/`に分類
  - **詳細**: `DIRECTORY_REORGANIZATION_COMPLETE.md`、`WORK_LOG.md`を参照
- ✅ **CLIツールの実装開始**（`tc-analyze`コマンド）
  - `tc_analyze/cli.py`: Typerベースのメインアプリケーション
  - データ管理コマンド: `data list`, `data info`, `data stats`
  - 設定管理コマンド: `config show`, `config validate`
  - 可視化コマンド: `center plot` (2d/3d対応)
  - setup.pyにエントリーポイント追加、システム全体で使用可能
- ✅ **utils/metadata.py作成**: .npz/.npyファイルのメタデータ読み込み
  - `read_data_metadata()`: ファイル形式、サイズ、shape、パラメータを取得
  - `get_data_statistics()`: min/max/mean/std/NaN数の計算
- ✅ **中心座標出力を.npz形式に統一**: メタデータ保存に対応
  - 2d: shape (nt, 2) - x, y座標を統合
  - 3d: shape (nt, nz, 2) - z面ごとの中心を保存
  - メタデータ: r_max_ite, max_iterations, convergence_threshold, actual_iterations
- ✅ **中心座標の柔軟な読み込み機能**: center_type ("2d"/"3d"), center_path を設定可能
  - setting.json、コマンドライン引数、コード内で指定可能
  - 優先順位: 引数 > コマンドライン > setting.json > デフォルト
  - 読み込み優先度: .npz > .npy > .txt（後方互換性維持）
- ✅ **utils/center.py作成**: 低気圧中心検出アルゴリズムを関数化
  - `find_pressure_center()`: 重み付き重心法、収束判定、iteration数を返す
  - `create_coordinate_meshgrid()`: 座標メッシュグリッド生成
- ✅ **ms_pres_center_calc.py作成**: 3次元圧力データから各z面の中心を検出
  - `--z-first`, `--z-last` でz面範囲を指定可能

#### 2025-11-27
- ✅ **物理定数の命名規則統一**: `g0`→`g`, `K_B`, `N_A`など（教科書表記に準拠）
- ✅ **utils/thermodynamics.py作成**: 相当温位計算を集約
- ✅ **utils/azimuthal.py作成**: 方位角平均計算を集約
- ✅ **utils/wind.py作成**: 風速場計算を集約
- ✅ **TC中心速度の自動計算**: 2次中心差分で自動計算（config依存削減）
- ✅ **UTILS_PHYSICS_REFERENCE.md作成**: 物理計算の包括的リファレンス

---

## 🎯 中心座標の柔軟な読み込み機能

### 設定方法

#### 1. setting.json での指定（推奨）
```json
{
  "center_type": "2d",
  "center_path": "center/ss_slp"
}
```

または3次元圧力データの場合：
```json
{
  "center_type": "3d",
  "center_path": "center/ms_pres"
}
```

#### 2. コマンドライン引数での指定
```bash
python script.py --center-type 3d --center-path center/ms_pres
```

#### 3. コード内での指定
```python
config = AnalysisConfig(center_type="3d", center_path="center/ms_pres")
```

### データ形式

#### 2d（デフォルト）
- ファイル: `{data_dir}/{center_path}/center.npz`（推奨）または `center.npy`
- shape: `(nt, 2)` - 全z面で同じ中心を使用
- アクセス: `config.center_x[t]`, `config.center_y[t]`
- メタデータ（.npz）: r_max_ite, max_iterations, convergence_threshold_x/y, actual_iterations

#### 3d
- ファイル: `{data_dir}/{center_path}/center.npz`（推奨）または `center.npy`
- shape: `(nt, nz, 2)` - z面ごとに異なる中心を使用
- アクセス: `config.center_x[t, z]`, `config.center_y[t, z]`
- メタデータ（.npz）: r_max_ite, max_iterations, convergence_threshold_x/y, actual_iterations, z_first, z_last

### 使用例

```python
from utils.config import AnalysisConfig

# デフォルト（ss_slp中心、2d）
config = AnalysisConfig()
center_x = config.center_x[t]  # shape: (nt,)

# ms_pres中心（3d）
config = AnalysisConfig(center_type="3d", center_path="center/ms_pres")
center_x = config.center_x[t, z]  # shape: (nt, nz)
```

### 後方互換性

旧形式のファイルも引き続きサポート：
- `x.txt`, `y.txt` (2d)
- `x_z000.txt`, `x_z001.txt`, ... (3d)
- `ss_slp_center_x.txt`, `ss_slp_center_y.txt` (古い形式)

---

## 🎯 タスク別参照先

| やりたいこと | 参照先 |
|------------|--------|
| **解析の実行順序を知りたい** | [ANALYSIS_WORKFLOW.md](./ANALYSIS_WORKFLOW.md) |
| **コマンド実行方法を知りたい** | [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) |
| **CLIツールを使いたい** | このページの「CLIツール」セクション、または `tc-analyze --help` |
| **データファイル情報を確認したい** | `tc-analyze data list/info/stats` コマンド |
| **設定を確認・検証したい** | `tc-analyze config show/validate` コマンド |
| **中心軌道をプロットしたい** | `tc-analyze center plot` コマンド |
| **システム構成を理解したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) |
| **物理計算・定数を確認したい** | [docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md) |
| **中心座標を指定したい** | このページの「中心座標の柔軟な読み込み機能」セクション |
| **TC中心を検出したい** | `utils.center.find_pressure_center()` を使用 |
| **新しい解析を追加したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) の拡張ガイド |
| **コーディング規約を確認したい** | [WORK_LOG.md](./WORK_LOG.md) の確立されたコーディングパターン |
| **エラーが発生した** | [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) のトラブルシューティング |
| **データフローを理解したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) のデータフロー |
| **グリッド計算を使いたい** | [WORK_LOG.md](./WORK_LOG.md) のグリッド生成の統一化 |
| **方位角平均を計算したい** | [docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md) の方位角平均計算 |
| **ディレクトリ構造を理解したい** | [DIRECTORY_REORGANIZATION_COMPLETE.md](./DIRECTORY_REORGANIZATION_COMPLETE.md) 参照 |
| **新しいパスメソッドを使いたい** | このページの「新しいパスメソッド」セクション |

## 📈 プロジェクト統計

- **総Pythonファイル数**: 224ファイル
- **総コード行数**: 21,900+行
- **utils**: 15ファイル、2,900+行（vorticity.py追加）
- **analysis**: 170ファイル、13,484行
  - calc: 54ファイル（ss_slp_center, ms_pres_center含む）
  - plot: 82ファイル
  - その他: 34ファイル
- **解析カテゴリ**: 7カテゴリ（whole_domain, vortex_region, azimuthal, vertical, center, diagnostics）
- **データ出力構造**: 3カテゴリ（domain, center, tc_centric）

---

**最終更新**: 2025-11-28
