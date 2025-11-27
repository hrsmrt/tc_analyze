# TC解析プロジェクトのコンテキスト

このプロジェクトは修士課程の研究で使用している熱帯低気圧の解析コード群です。

**プロジェクト規模**: 222ファイル、21,707行（Python）

---

## 📚 主要ドキュメント

### 必須ドキュメント（優先度順）

1. **プロジェクト概要**
   @./README.md
   - 全体像、環境構築、クイックスタート

2. **コマンドリファレンス（よく使うコマンド）**
   @./docs/COMMAND_REFERENCE.md
   - analyze.shの使い方、トラブルシューティング

3. **アーキテクチャ設計書**
   @./docs/ARCHITECTURE.md
   - システム構成、データフロー、拡張ガイド

4. **物理計算リファレンス（NEW! 2025-11-27）**
   @./docs/UTILS_PHYSICS_REFERENCE.md
   - utils内の全物理定数（Cp, Rd, g, PRES_Sなど）
   - 熱力学計算（温位θ、相当温位θ_e）
   - 風速場計算、方位角平均、流線関数など

5. **作業履歴とコーディング規約**
   @./docs/WORK_LOG.md
   - 確立されたコーディングパターン
   - グリッド生成、ビニング方法の統一

### 補足ドキュメント

6. **リファクタリング概要**
   @./archive/docs/REFACTORING_SUMMARY.md

7. **マイグレーション完了報告**
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

### utilsモジュール（13ファイル、2,679行）
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
```

### 物理定数の命名規則（2025-11-27統一）
- **普遍定数**: `K_B`, `N_A` (大文字+アンダースコア)
- **物理記号**: `Cp`, `Rd`, `Rv`, `Lv`, `g` (教科書表記)
- **複合語**: `PRES_S`, `G_MS`, `G_ME` (大文字+アンダースコア)

### ディレクトリ構成
```
tc_analyze/
├── utils/          # 共通モジュール（13ファイル、2,679行）
│   ├── config.py, grid.py, plotting.py  # コア機能
│   ├── center.py                        # 中心検出アルゴリズム
│   ├── basic.py, thermodynamics.py      # 物理定数・計算
│   ├── wind.py, azimuthal.py            # 風速・方位角平均
│   └── streamfunction.py                # 流線関数
├── analysis/       # 解析スクリプト（170ファイル、13,484行）
│   ├── whole_domain/  # 領域全体（31、中心位置非依存: 3d: 19, 2d: 12）
│   ├── vortex_region/ # 渦領域（25、中心位置依存: 3d: 18, 2d: 7）
│   ├── azimuthal/ # 方位角解析（basic: 56, eliassen: 16, momentum: 22, q8: 5）
│   ├── vertical/  # 鉛直解析（profile: 4, q4: 4）
│   ├── center/    # TC中心位置計算（9: ss_slp, ms_pres, utils/center使用）
│   └── diagnostics/ # 診断解析（sums: 4, symmetrisity: 4）
├── docs/           # ドキュメント
│   ├── COMMAND_REFERENCE.md, ARCHITECTURE.md, WORK_LOG.md
│   └── UTILS_PHYSICS_REFERENCE.md  # 物理計算リファレンス
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
- ✅ **中心座標の柔軟な読み込み機能**: center_type ("2d"/"3d"), center_path を設定可能
  - setting.json、コマンドライン引数、コード内で指定可能
  - 優先順位: 引数 > コマンドライン > setting.json > デフォルト
- ✅ **utils/center.py作成**: 低気圧中心検出アルゴリズムを関数化
  - `find_pressure_center()`: 重み付き重心法による汎用関数
  - `create_coordinate_meshgrid()`: 座標メッシュグリッド生成
- ✅ **ms_pres_center_calc.py作成**: 3次元圧力データから各z面の中心を検出
  - `--z-first`, `--z-last` でz面範囲を指定可能
- ✅ **中心座標出力の統一**: .npy形式 (2d: nt×2, 3d: nt×nz×2)
  - 1ファイルに x, y 座標を統合
  - I/O効率の向上
- ✅ **後方互換性の維持**: 旧形式(.txt)も引き続きサポート

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
- ファイル: `{data_dir}/{center_path}/center.npy`
- shape: `(nt, 2)` - 全z面で同じ中心を使用
- アクセス: `config.center_x[t]`, `config.center_y[t]`

#### 3d
- ファイル: `{data_dir}/{center_path}/center.npy`
- shape: `(nt, nz, 2)` - z面ごとに異なる中心を使用
- アクセス: `config.center_x[t, z]`, `config.center_y[t, z]`

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
| **コマンド実行方法を知りたい** | [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) |
| **システム構成を理解したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) |
| **物理計算・定数を確認したい** | [docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md) |
| **中心座標を指定したい** | このページの「中心座標の柔軟な読み込み機能」セクション |
| **TC中心を検出したい** | `utils.center.find_pressure_center()` を使用 |
| **新しい解析を追加したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) の拡張ガイド |
| **コーディング規約を確認したい** | [docs/WORK_LOG.md](./docs/WORK_LOG.md) の確立されたコーディングパターン |
| **エラーが発生した** | [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) のトラブルシューティング |
| **データフローを理解したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) のデータフロー |
| **グリッド計算を使いたい** | [docs/WORK_LOG.md](./docs/WORK_LOG.md) のグリッド生成の統一化 |
| **方位角平均を計算したい** | [docs/UTILS_PHYSICS_REFERENCE.md](./docs/UTILS_PHYSICS_REFERENCE.md) の方位角平均計算 |

## 📈 プロジェクト統計

- **総Pythonファイル数**: 223ファイル
- **総コード行数**: 21,842行
- **utils**: 13ファイル、2,679行
- **analysis**: 170ファイル、13,484行
  - calc: 54ファイル（ss_slp_center, ms_pres_center含む）
  - plot: 82ファイル
  - その他: 34ファイル
- **解析カテゴリ**: 7カテゴリ（whole_domain, vortex_region, azimuthal, vertical, center, diagnostics）

---

**最終更新**: 2025-11-28
