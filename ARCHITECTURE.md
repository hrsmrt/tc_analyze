# アーキテクチャ設計書

## 📋 目次
- [システム概要](#システム概要)
- [アーキテクチャ図](#アーキテクチャ図)
- [データフロー](#データフロー)
- [モジュール設計](#モジュール設計)
- [ディレクトリ構造](#ディレクトリ構造)
- [設計原則](#設計原則)
- [拡張ガイド](#拡張ガイド)

---

## 🎯 システム概要

### プロジェクトの目的

熱帯低気圧（TC）の3次元直交座標データを解析し、以下を実現する：

1. **中心位置の自動検出** - 海面気圧の最小値から台風中心を追跡
2. **多次元解析** - 3次元場、2次元場、鉛直プロファイル、方位角平均
3. **可視化** - 時系列プロット、等高線図、ベクトル場の描画
4. **並列処理** - 大規模データを効率的に処理
5. **再現性** - 設定ファイルによる一元管理

### 技術スタック

| 項目 | 技術 | バージョン |
|------|------|-----------|
| 言語 | Python | >= 3.8 |
| 数値計算 | NumPy | latest |
| 可視化 | Matplotlib | latest |
| 並列処理 | Joblib | latest |
| パッケージ管理 | setuptools | latest |

### システムの特徴

- ✅ **モジュール化** - 共通機能を`utils/`パッケージに集約
- ✅ **設定管理** - JSON形式の設定ファイルで一元管理
- ✅ **並列処理** - 時間ステップごとに並列実行
- ✅ **大規模データ対応** - メモリマップドファイルで効率的に処理
- ✅ **拡張性** - プラグイン的に解析スクリプトを追加可能

---

## 🏗️ アーキテクチャ図

### 全体構成

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TC Analyze System                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐                                 │
│  │ Input Data   │     │ Config File  │                                 │
│  │  *.grd       │     │ setting.json │                                 │
│  │ (Fortran)    │     └──────┬───────┘                                 │
│  └──────┬───────┘            │                                         │
│         │                    │                                         │
│         │        ┌───────────▼───────────┐                             │
│         │        │   AnalysisConfig      │                             │
│         │        │   (utils/config.py)   │                             │
│         │        └───────────┬───────────┘                             │
│         │                    │                                         │
│         │        ┌───────────▼───────────┐                             │
│         │        │   GridHandler         │                             │
│         │        │   (utils/grid.py)     │                             │
│         │        └───────────────────────┘                             │
│         │                                                               │
│         ├─────────────────┐                                            │
│         │                 │                                            │
│         ▼                 ▼                                            │
│  ┌──────────────┐  ┌──────────────────────────────────────┐           │
│  │ Pattern 1:   │  │ Pattern 2: Direct Plot               │           │
│  │ 2-Stage      │  │ (2d/whole_domain.py 等)               │           │
│  │ Processing   │  │                                      │           │
│  └──────────────┘  │  ┌────────────────────────────────┐ │           │
│         │          │  │  1. Load data (memmap)         │ │           │
│         │          │  │  2. Create plots directly      │ │           │
│         │          │  │  3. Save figures (*.png)       │ │           │
│         │          │  └────────────────────────────────┘ │           │
│         │          └──────────────┬───────────────────────┘           │
│         ▼                         │                                   │
│  ┌─────────────────────────────────────────────┐     │                │
│  │         Calculation Scripts                 │     │                │
│  │         (*_calc.py)                         │     │                │
│  │  ┌──────────────────────────────────────┐   │     │                │
│  │  │  1. Load data (memmap)               │   │     │                │
│  │  │  2. Process (parallel)               │   │     │                │
│  │  │  3. Save results (*.npy)             │   │     │                │
│  │  └──────────────────────────────────────┘   │     │                │
│  └─────────────────┬───────────────────────────┘     │                │
│                    │                                 │                │
│                    ▼                                 │                │
│         ┌──────────────────┐                         │                │
│         │  Data Storage    │                         │                │
│         │  data/*.npy      │                         │                │
│         └──────────┬───────┘                         │                │
│                    │                                 │                │
│                    ▼                                 │                │
│  ┌─────────────────────────────────────────────┐    │                │
│  │         Plotting Scripts                    │    │                │
│  │         (*_plot.py)                         │    │                │
│  │  ┌──────────────────────────────────────┐   │    │                │
│  │  │  1. Load data (*.npy)                │   │    │                │
│  │  │  2. Create plots                     │   │    │                │
│  │  │  3. Save figures (*.png)             │   │    │                │
│  │  └──────────────────────────────────────┘   │    │                │
│  │  ┌──────────────────────────────────────┐   │    │                │
│  │  │   PlotConfig (utils/plotting.py)     │   │    │                │
│  │  └──────────────────────────────────────┘   │    │                │
│  └─────────────────┬───────────────────────────┘    │                │
│                    │                                │                │
│                    ▼                                ▼                │
│                    └────────────┬────────────────────┘                │
│                                 ▼                                     │
│                      ┌──────────────────┐                            │
│                      │  Figure Output   │                            │
│                      │  fig/*.png       │                            │
│                      └──────────────────┘                            │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────┐
        │  Orchestration Layer             │
        │  script/analyze.sh               │
        │  - Category management           │
        │  - Style handling                │
        │  - Logging                       │
        └──────────────────────────────────┘
```

### レイヤー構成

```
┌─────────────────────────────────────────┐
│  Orchestration Layer                    │  ← analyze.sh
│  (Category management, Logging)         │
├─────────────────────────────────────────┤
│  Application Layer                      │  ← *_calc.py, *_plot.py
│  (Analysis scripts, Plotting scripts)   │
├─────────────────────────────────────────┤
│  Service Layer                          │  ← utils/
│  (Config, Grid, Plotting)               │
├─────────────────────────────────────────┤
│  Data Layer                             │  ← .grd, .npy, .png
│  (Input, Intermediate, Output)          │
└─────────────────────────────────────────┘
```

---

## 🔄 データフロー

### 基本的なデータフロー

システムには2つのデータフローパターンが存在します：

#### パターン1: 2段階処理（計算→可視化）

中間データを保存し、後から繰り返しプロット可能。方位角平均などの複雑な処理に使用。

```
[入力データ]          [計算処理]           [中間データ]        [可視化]           [出力図]

ms_u.grd    ──┐
ms_v.grd    ──┤→ divergence_  →  data/3d/      →  divergence_  → fig/3d/
ms_w.grd    ──┘   calc.py         divergence/      whole_domain_   whole_domain/
...                               div_t*.npy        plot.py         divergence/
                                                                    t*.png

[Fortran Binary]  [Python Script]  [NumPy Binary]  [Python Script]  [PNG Image]
 Big-endian       Parallel         Compressed      Matplotlib       Optimized
 ~GB size         Processing       ~MB size        Styling          ~KB size

例: 方位角平均解析、発散・渦度計算、相対風計算など
```

#### パターン2: 直接プロット

中間データを保存せず、入力データから直接プロット。単純な可視化に使用。

```
[入力データ]          [可視化]                       [出力図]

ms_u.grd    ──┐
ms_v.grd    ──┤→ whole_domain.py  →  fig/2d/whole_domain/
ss_slp.grd  ──┘   (memmap)            ms_u/t*.png
...                                    ms_v/t*.png
                                       ss_slp/t*.png

[Fortran Binary]  [Python Script]                  [PNG Image]
 Big-endian       Matplotlib                       Optimized
 ~GB size         Direct rendering                 ~KB size

例: 2d/whole_domain.py, 3d/whole_domain_plot.py など
   生の.grdファイルを直接読み込んでプロット
```

### 詳細なデータフロー（方位角平均の例）

```
1. 入力データの読み込み
   ├─ ms_u.grd, ms_v.grd (3D wind field)
   └─ ss_slp_center_*.txt (TC center position)

2. 中心座標の取得
   └─ AnalysisConfig.center_x[t], center_y[t]

3. 極座標変換
   ├─ GridHandler.calculate_radial_distance(cx, cy)
   └─ GridHandler.uv_to_radial_tangential(u, v, cx, cy)

4. ビニング（方位角平均）
   ├─ bin_idx = np.floor(R / dx).astype(int)
   ├─ azim_sum[z, bin_idx] += data[z, y, x]
   └─ azim_mean[z, r] = azim_sum / count

5. データ保存
   └─ data/azim/relative_wind_radial/t*.npy

6. プロット生成
   ├─ grid.create_radial_vertical_meshgrid(R_MAX)
   ├─ ax.contourf(r_mesh, z_mesh, data)
   └─ fig.savefig(fig/azim/relative_wind_radial/t*.png)
```

### データサイズの変遷

#### パターン1: 2段階処理の場合

```
段階                  形状                       サイズ           ファイル数
────────────────────────────────────────────────────────────────────────
入力 (.grd)           (nt, nz, ny, nx)          ~2 GB/変数       ~30個
                      (101, 74, 128, 128)

計算 (メモリ)         (nz, ny, nx)              ~5 MB/時刻       ─
                      (74, 128, 128)

中間 (.npy)           (nz, nr)                  ~50 KB/時刻      ~100個
方位角平均             (74, 1000)

出力 (.png)           図として保存               ~100 KB/図       ~1000個
多層、複数変数
```

#### パターン2: 直接プロットの場合

```
段階                  形状                       サイズ           ファイル数
────────────────────────────────────────────────────────────────────────
入力 (.grd)           (nt, nz, ny, nx)          ~2 GB/変数       ~30個
                      (101, 74, 128, 128)

メモリマップ          (nz, ny, nx)              0 (ディスク)     ─
                      (74, 128, 128)

出力 (.png)           図として保存               ~100 KB/図       ~1000個
多層、複数変数

※中間データを保存しないため、ディスクI/Oは入力と出力のみ
```

---

## 🧩 モジュール設計

### コアモジュール（utils/）

#### 1. config.py - 設定管理

**役割**: setting.jsonの読み込みと設定値の提供

**主要クラス**:
```python
class AnalysisConfig:
    # 基本設定（setting.jsonから直接）
    glevel: int          # グリッドレベル
    nt: int              # 時間ステップ数
    t_first: int         # 開始時刻
    t_last: int          # 終了時刻

    # 計算された設定
    nx: int              # = 2^glevel
    ny: int              # = 2^glevel
    dx: float            # グリッド間隔 x
    dy: float            # グリッド間隔 y

    # パス管理
    get_data_path(*paths) -> str
    get_fig_path(*paths) -> str

    # TC中心座標（キャッシュ付き）
    center_x: np.ndarray
    center_y: np.ndarray
```

**設計判断**:
- プロパティを使用して計算値を遅延評価
- パス生成はメソッドで統一（ハードコード排除）
- 中心座標はキャッシュして再読み込みを防止

#### 2. grid.py - グリッド計算

**役割**: 座標系の変換、グリッド生成、距離・角度計算

**主要クラス**:
```python
class GridHandler:
    # メッシュグリッド（初期化時に生成）
    X: np.ndarray        # (ny, nx)
    Y: np.ndarray        # (ny, nx)

    # 座標変換
    calculate_theta(cx, cy) -> np.ndarray
    calculate_radial_distance(cx, cy) -> np.ndarray
    uv_to_radial_tangential(u, v, cx, cy) -> (v_r, v_t)

    # 渦領域抽出
    extract_vortex_region(data, cx, cy, extent) -> np.ndarray

    # 方位角平均用グリッド
    create_radial_vertical_meshgrid(r_max, nz=None) -> (r, z)
```

**設計判断**:
- 周期境界条件を自動適用
- ブロードキャストを活用して高速化
- 3D/2Dデータに自動対応

#### 3. plotting.py - プロット設定

**役割**: 変数ごとのプロット設定、スタイル管理

**主要クラス**:
```python
class PlotConfig:
    # 変数設定の辞書
    VARIABLE_CONFIGS = {
        "sa_lh_sfc": {
            "levels": np.arange(0, 500, 10),
            "cmap": "rainbow",
            "title": "潜熱流束",
            "extend": "both"
        },
        ...
    }

    # プロット作成
    create_contourf(ax, X, Y, data, varname, time_hour)

    # カスタム設定追加
    add_variable(varname, levels, cmap, title)
```

**関数**:
```python
# スタイルシート解析
parse_style_argument() -> str

# カスタムカラーマップ
create_custom_colormap(base_cmap, n_white_colors) -> ListedColormap
```

**設計判断**:
- 変数設定を辞書で一元管理（300+行のmatch文を削減）
- 環境変数とコマンドライン引数の両方に対応
- プラグイン的に新規変数を追加可能

### スクリプト設計パターン

#### 計算スクリプト (*_calc.py)

```python
"""
標準的な計算スクリプトのパターン
"""
import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定とグリッド
config = AnalysisConfig()
grid = GridHandler(config)

# 出力先
OUTPUT_FOLDER = config.get_data_path("category", "variable")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 入力データ（メモリマップド）
data_all = np.memmap(
    f"{config.input_folder}/input.grd",
    dtype=">f4",  # Big-endian float32
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx)
)

def process_t(t):
    """単一時刻の処理"""
    data = data_all[t]

    # 処理...
    result = calculate_something(data)

    # 保存
    np.save(f"{OUTPUT_FOLDER}/t{str(t).zfill(3)}.npy", result)
    print(f"t: {t} done")

# 並列実行
Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1)
)
```

**重要な点**:
- メモリマップドファイルで大規模データに対応
- joblibで時間ステップごとに並列処理
- 型は常に`>f4`（Big-endian float32）を明示

#### プロットスクリプト (*_plot.py)

```python
"""
標準的なプロットスクリプトのパターン
"""
import os
import matplotlib
matplotlib.use('Agg')  # GUI不要、高速化
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルとグリッド
mpl_style_sheet = parse_style_argument()
config = AnalysisConfig()
grid = GridHandler(config)

# データから実際のサイズを取得（重要！）
sample_data = np.load(f"{config.get_data_path('category', 'variable')}/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

# 出力先
OUTPUT_FOLDER = config.get_fig_path("category", "variable")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_t(t):
    """単一時刻のプロット"""
    data = np.load(f"{config.get_data_path('category', 'variable')}/t{str(t).zfill(3)}.npy")

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(r_mesh * 1e-3, z_mesh * 1e-3, data, cmap="rainbow", extend="both")
    fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20])
    ax.set_title(f"Title t = {config.time_list[t]} hour")
    fig.savefig(f"{OUTPUT_FOLDER}/t{str(t).zfill(3)}.png")
    plt.close()

# 並列実行
Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1)
)
```

**重要な点**:
- `matplotlib.use('Agg')`でGUIオーバーヘッドを削減
- データサイズは理論値でなく実データから取得
- `plt.close()`でメモリリークを防止

#### 直接プロットスクリプト (パターン2)

中間データを保存せず、入力データから直接プロット。

```python
"""
直接プロットスクリプトのパターン
例: 2d/whole_domain.py
"""
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import PlotConfig, parse_style_argument

# コマンドライン引数の解析
VARNAME = sys.argv[1]  # 変数名を引数で受け取る
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()
grid = GridHandler(config)

# 出力先
OUTPUT_DIR = config.get_fig_path("2d", "whole_domain", VARNAME)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 入力データ（メモリマップド）- ★直接.grdファイルを読み込む
data_all = np.memmap(
    f"{config.input_folder}{VARNAME}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx)  # 2次元データの場合
)

X_km, Y_km = grid.get_meshgrid_km()

def process_t(t):
    """単一時刻のプロット"""
    data = data_all[t]  # ★メモリマップから直接読み込み

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 4))

    # PlotConfigを使ってプロット
    c, title = PlotConfig.create_contourf(
        ax, X_km, Y_km, data, VARNAME, config.time_list[t]
    )
    ax.set_title(title)
    fig.colorbar(c, ax=ax)
    ax.set_aspect("equal", "box")

    # ★直接PNG保存（中間データなし）
    fig.savefig(f"{OUTPUT_DIR}/t{str(t).zfill(3)}.png")
    plt.close()

# 並列実行
Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1)
)
```

**重要な点**:
- ★ `.grd`ファイルを直接メモリマップで読み込む
- ★ 中間データ（`.npy`）を保存しない
- プロットスタイルを変更したい場合は再実行が必要
- ディスクI/Oが少なく高速（計算処理が不要な場合）

**使い分けの基準**:

| 条件 | パターン1（2段階） | パターン2（直接） |
|------|------------------|-----------------|
| 複雑な計算が必要 | ✅ 推奨 | ❌ 不適 |
| スタイル変更を頻繁に行う | ✅ 推奨 | ❌ 毎回再計算 |
| シンプルな可視化のみ | △ 可能 | ✅ 推奨 |
| ディスク容量が限られている | △ 中間データが増える | ✅ 推奨 |
| データを再利用したい | ✅ 推奨 | ❌ 不可 |

---

## 📂 ディレクトリ構造

### プロジェクトルート

```
tc_analyze/
├── utils/                    # 共通モジュール（パッケージ化）
│   ├── __init__.py
│   ├── config.py            # 設定管理
│   ├── grid.py              # グリッド計算
│   ├── plotting.py          # プロット設定
│   └── basic.py             # 物理定数
│
├── script/                   # 実行スクリプト
│   ├── analyze.sh           # 統合実行スクリプト（最重要）
│   ├── analyze_all.sh       # 全カテゴリ実行
│   └── setting.json         # 設定ファイル（サンプル）
│
├── 3d/                       # 3次元解析（60+スクリプト）
│   ├── divergence_calc.py
│   ├── divergence_whole_domain_plot.py
│   ├── divergence_vortex_region_plot.py
│   └── ...
│
├── 2d/                       # 2次元解析
│   ├── whole_domain.py
│   ├── vortex_region.py
│   └── ...
│
├── azim_mean/                # 方位角平均解析（94スクリプト）
│   ├── azim_wind_calc.py
│   ├── azim_wind_radial_plot.py
│   ├── eliassen/            # Eliassen方程式関連
│   ├── eq_momentum_u/       # 運動量方程式（u成分）
│   └── eq_momentum_w/       # 運動量方程式（w成分）
│
├── azim_q8/                  # 8方位分割解析
├── center/                   # TC中心位置計算
├── sums/                     # 積算値計算
├── symmetrisity/             # 対称性解析
├── z_profile/                # 鉛直プロファイル
├── z_profile_q4/             # 鉛直プロファイル（4象限）
│
├── archive/                  # アーカイブ
│   ├── backups/
│   └── migration_scripts/
│
├── setup.py                  # パッケージ設定
├── README.md                 # プロジェクト概要
├── ARCHITECTURE.md           # このファイル
├── COMMAND_REFERENCE.md      # コマンドリファレンス
├── WORK_LOG.md               # 作業ログ・コーディングパターン
├── MIGRATION_COMPLETE.md     # リファクタリング報告
└── CLAUDE.md                 # AI支援用コンテキスト
```

### データディレクトリ（作業ディレクトリ）

```
workdir/                      # setting.jsonがある場所で実行
├── setting.json             # 設定ファイル（必須）
│
├── data/                     # 計算結果（.npyファイル）
│   ├── ss_slp_center_x.txt  # TC中心x座標
│   ├── ss_slp_center_y.txt  # TC中心y座標
│   ├── 3d/
│   │   ├── divergence/
│   │   │   ├── div_t000.npy
│   │   │   ├── div_t001.npy
│   │   │   └── ...
│   │   └── ...
│   ├── azim/
│   │   ├── relative_wind_radial/
│   │   │   ├── t000.npy
│   │   │   └── ...
│   │   └── ...
│   └── ...
│
└── fig/                      # プロット結果（.pngファイル）
    ├── 3d/
    │   ├── whole_domain/
    │   │   └── divergence/
    │   │       ├── z00/
    │   │       │   ├── t000.png
    │   │       │   └── ...
    │   │       └── ...
    │   └── vortex_region/
    │       └── ...
    ├── azim/
    │   ├── relative_wind_radial/
    │   │   ├── t000.png
    │   │   └── ...
    │   └── ...
    └── ...
```

---

## 🎨 設計原則

### 1. DRY（Don't Repeat Yourself）

**問題**: 150+ファイルで同じ設定読み込みコードが重複
```python
# ❌ 悪い例（移行前）
with open('setting.json') as f:
    setting = json.load(f)
glevel = setting['glevel']
nx = 2 ** glevel
dx = triangle_size / nx
# ... 各ファイルで20-30行
```

**解決**: 共通モジュールに集約
```python
# ✅ 良い例（移行後）
from utils.config import AnalysisConfig
config = AnalysisConfig()
# config.nx, config.dx など全てアクセス可能
```

**効果**: **85-90%のコード削減**

### 2. 単一責任の原則（Single Responsibility）

各モジュールは明確な責任を持つ：

| モジュール | 責任 |
|-----------|------|
| `config.py` | 設定の読み込みと提供のみ |
| `grid.py` | グリッド計算と座標変換のみ |
| `plotting.py` | プロット設定の管理のみ |
| `*_calc.py` | データ計算と保存のみ |
| `*_plot.py` | データ読み込みと可視化のみ |

### 3. 設定より規約（Convention over Configuration）

**確立された規約**:

```python
# ファイル命名規約
data/category/variable/t{t:03d}.npy     # 計算結果
fig/category/region/variable/t{t:03d}.png  # プロット結果

# 関数命名規約
process_t(t)                            # 単一時刻の処理
calculate_*()                           # 計算関数
create_*()                              # 生成関数

# ビニング計算の規約（必須）
bin_idx = np.floor(R / config.dx).astype(int)
max_bin = int(np.floor(r_max / config.dx))
bin_idx = np.clip(bin_idx, 0, max_bin - 1)
count = np.bincount(bin_idx, minlength=max_bin)
```

### 4. データ駆動設計（Data-Driven Design）

グリッドサイズは理論値でなく実データから取得：

```python
# ❌ 悪い例
nr = int(r_max / config.dx)  # 理論値
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(r_max)

# ✅ 良い例
sample_data = np.load(f"data/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]  # 実データから取得
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)
```

**理由**: `//` と `np.floor()` の微妙な違いによるサイズ不一致を防止

### 5. 性能最適化

#### ベクトル化
```python
# ❌ 遅い（Zループ）
for z in range(config.nz):
    du_dx[z] = (np.roll(data_u[z], -1, axis=1) - ...) / (2 * dx)

# ✅ 速い（5-10倍）
du_dx = (np.roll(data_u, -1, axis=2) - ...) / (2 * dx)
```

#### メモリ最適化
```python
# ✅ メモリマップドファイル（GBサイズも扱える）
data_all = np.memmap(
    "input.grd",
    dtype=">f4",
    mode="r",
    shape=(nt, nz, ny, nx)
)

# ✅ matplotlib Aggバックエンド（GUIオーバーヘッド削減）
import matplotlib
matplotlib.use('Agg')
```

---

## 🚀 拡張ガイド

### 新しい解析変数の追加

#### ステップ1: 計算スクリプトの作成

```python
# 3d/new_variable_calc.py

import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig

config = AnalysisConfig()

# 出力先
OUTPUT_FOLDER = config.get_data_path("3d", "new_variable")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 入力データ
data_all = np.memmap(
    f"{config.input_folder}/input.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx)
)

def process_t(t):
    data = data_all[t]

    # 計算処理
    result = your_calculation(data)

    # 保存
    np.save(f"{OUTPUT_FOLDER}/t{str(t).zfill(3)}.npy", result)
    print(f"t: {t} done")

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1)
)
```

#### ステップ2: プロットスクリプトの作成

```python
# 3d/new_variable_whole_domain_plot.py

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, PlotConfig

mpl_style_sheet = parse_style_argument()
config = AnalysisConfig()
grid = GridHandler(config)

OUTPUT_DIR = config.get_fig_path("3d", "whole_domain", "new_variable")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# プロット設定を追加（オプション）
PlotConfig.add_variable(
    "new_variable",
    levels=np.arange(0, 100, 10),
    cmap="rainbow",
    title="新しい変数",
    extend="both"
)

def process_t(t):
    data = np.load(f"{config.get_data_path('3d', 'new_variable')}/t{str(t).zfill(3)}.npy")
    X_km, Y_km = grid.get_meshgrid_km()

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 4))

    # PlotConfigを使う場合
    c, title = PlotConfig.create_contourf(ax, X_km, Y_km, data[z], "new_variable", config.time_list[t])
    ax.set_title(title)

    # または手動で設定
    # c = ax.contourf(X_km, Y_km, data[z], levels=..., cmap=..., extend=...)

    fig.colorbar(c, ax=ax)
    fig.savefig(f"{OUTPUT_DIR}/t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1)
)
```

#### ステップ3: analyze.shに登録（オプション）

```bash
# script/analyze.shに追加

# 3dカテゴリの中に追加
case "$category" in
    3d)
        # ... 既存のスクリプト
        run_script "3d/new_variable_calc.py"
        run_script "3d/new_variable_whole_domain_plot.py" "$style"
        ;;
esac
```

### 新しい解析カテゴリの追加

1. **ディレクトリ作成**
   ```bash
   mkdir tc_analyze/new_category
   ```

2. **スクリプト作成**（上記パターンに従う）

3. **analyze.shに登録**
   ```bash
   # カテゴリリストに追加
   CATEGORIES="... new_category"

   # case文に追加
   case "$category" in
       new_category)
           run_script "new_category/calc.py"
           run_script "new_category/plot.py" "$style"
           ;;
   esac
   ```

### 設定値の追加

```json
// setting.json
{
    "existing_settings": "...",
    "new_parameter": 123.45
}
```

```python
# utils/config.py

class AnalysisConfig:
    @property
    def new_parameter(self) -> float:
        """新しいパラメータ"""
        return self._data.get("new_parameter", default_value)
```

---

## 📚 参考資料

### 関連ドキュメント

- [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md) - コマンドリファレンス
- [WORK_LOG.md](./WORK_LOG.md) - コーディングパターンと作業履歴
- [MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md) - リファクタリング完了報告

### コーディング規約

詳細は[WORK_LOG.md](./WORK_LOG.md)を参照：
- 標準的なプロットファイルの構造
- 標準的な計算ファイルの構造
- ビニング計算の注意点
- 座標系の種類（cell center, cell wall, shifted cell center）

### 既知の問題と解決策

[WORK_LOG.md](./WORK_LOG.md)の「既知の問題と解決済み問題」セクションを参照：
- TypeError: Shapes do not match
- データサイズの不一致
- IndexError: index is out of bounds

---

**最終更新日**: 2025-11-27
**バージョン**: 1.0
**著者**: TC Analyze Development Team
