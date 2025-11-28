# tc_analyze プロジェクト作業ログ

## 最終更新日: 2025-11-28

---

## 最新の変更 (2025-11-28)

### ディレクトリ再編成の完了

全170個のPythonファイルを新しいディレクトリ構造にマイグレーション完了。

#### 主な成果
1. **3つのカテゴリへの明確な分類**
   - `domain/` - 中心非依存データ（全領域解析）
   - `center/` - 中心座標データ
   - `tc_centric/` - TC相対座標系データ（中心依存）

2. **新しいパスメソッドの追加** (`utils/config.py`)
   - `get_domain_path()` - 中心非依存データのパス生成
   - `get_center_path()` - 中心座標データのパス生成
   - `get_tc_centric_path()` - TC相対座標系データのパス生成

3. **渦度計算の共通化** (`utils/vorticity.py`)
   - `calculate_vorticity_z()` - z方向渦度計算
   - 重複コード52行削減
   - オンデマンド計算でストレージ節約

4. **流線関数プロットのオンデマンド化**
   - u/v → 渦度 → 流線関数を全て実行時計算
   - 数GB〜数百GBのストレージ節約

5. **相対風の正しい分類**
   - TC移動速度に依存する相対風を`tc_centric/`に分類
   - ユーザーの明示的な指示に基づく

詳細: `DIRECTORY_REORGANIZATION_COMPLETE.md`

---

## 過去の主要な作業

### 2025-11-13: グリッド生成の統一化

#### `utils/grid.py` の拡張
- `create_radial_vertical_meshgrid(r_max, nz=None)` に `nz` パラメータを追加
- z方向のグリッド数を指定可能にし、微分後のデータ（nz-1）に対応

#### 修正ファイル（計54ファイル）
- **azim_mean/** (26ファイル): プロット16、計算10
- **azim_mean/eliassen/** (10ファイル): プロット8、計算2
- **azim_mean/eq_momentum_u/** (5ファイル)
- **azim_q8/** (5ファイル): 計算2、プロット3
- **sums/** (2ファイル): setting.json → AnalysisConfig に移行
- **symmetrisity/** (6ファイル): IndexError修正、GridHandler使用

詳細: `REFACTORING_SUMMARY.md`, `MIGRATION_COMPLETE.md`

---

## 確立されたコーディングパターン

### 標準的なプロットファイルの構造

```python
import os
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)
mpl_style_sheet = parse_style_argument()

# データから実際のサイズを取得
sample_data = np.load(...)
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

output_folder = config.get_tc_centric_path("azimuthal", "basic/wind", data_type="fig")
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(...)
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(r_mesh * 1e-3, z_mesh * 1e-3, data, cmap="rainbow", extend="both")
    fig.colorbar(c, ax=ax)
    ax.set_title(f"タイトル t = {config.time_list[t]} hour")
    fig.savefig(f"{output_folder}/t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
```

### 標準的な計算ファイルの構造

```python
import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3
output_folder = config.get_tc_centric_path("azimuthal", "basic/wind")
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    cx = config.center_x[t]
    cy = config.center_y[t]

    R = grid.calculate_radial_distance(cx, cy)
    mask = R <= r_max
    valid_r = R[mask]

    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    azim_sum = np.zeros((config.nz, max_bin))
    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ処理...

    np.save(f"{output_folder}/t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
```

---

## 重要な注意事項

### ディレクトリ構造とパス生成

#### 1. 中心非依存データ (domain)
全領域解析や領域平均など、TC中心に依存しないデータ

```python
config.get_domain_path("whole_domain", "2d/ss_slp_min")
config.get_domain_path("whole_domain", "3d/vorticity_z")
config.get_domain_path("vertical", "profile")
```

#### 2. 中心座標データ (center)
TC中心座標そのもの

```python
config.get_center_path("ss_slp")
config.get_center_path("ms_pres")
```

#### 3. TC相対座標系データ (tc_centric)
TC中心を基準とした相対座標系の解析（中心依存）

```python
config.get_tc_centric_path("azimuthal", "basic/wind")
config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_radial")  # 相対風
config.get_tc_centric_path("vertical", "q4/zeta")
config.get_tc_centric_path("diagnostics", "symmetrisity")
```

### データ形状の特殊ケース

1. **z方向微分データ (N2, du_dr, wdu_dz など)**
   - 形状: `(config.nz - 1, nr)`
   - プロット時に `nz=nz_data` を指定する必要がある

2. **azim_q8 データ**
   - 形状: `(nz, nr, 8)` - 8セクターに分割
   - 各セクターごとに個別にプロット

3. **shifted cell center (eq_momentum_u の一部)**
   - grad_p, gradient_wind_eq, gradient_balance_score
   - rgrid = `((np.arange(nr_data) + 1) * config.dx + config.dx / 2) * 1e-3`

### ビニング計算の注意点

- **必ず `np.floor()` を使用** - `//` 演算子は使わない
- **必ず `np.clip()` でインデックスを制限**
- **必ず `minlength=max_bin` を指定**

```python
# 正しい方法
bin_idx = np.floor(valid_r / config.dx).astype(int)
max_bin = int(np.floor(r_max / config.dx))
bin_idx = np.clip(bin_idx, 0, max_bin - 1)

# 間違った方法
bin_idx = (valid_r // config.dx).astype(int)  # NG
```

### 渦度計算

**必ず共通関数を使用**:

```python
from utils.vorticity import calculate_vorticity_z

# 2D or 3D data
vorticity_z = calculate_vorticity_z(u, v, config.dx, config.dy)
```

- 周期境界条件を考慮
- 北極・南極での境界条件を考慮
- ベクトル化により5-10倍高速

---

## 重要なファイル

### 設定とユーティリティ
- `utils/config.py` - 設定管理（**パスメソッド追加**）
- `utils/grid.py` - グリッド生成
- `utils/plotting.py` - プロット関連ユーティリティ
- `utils/basic.py` - 物理定数と基本関数
- `utils/vorticity.py` - **渦度計算（新規追加）**
- `utils/streamfunction.py` - 流線関数計算

### グリッド設定
- `config.dx` - x方向グリッド間隔
- `config.dy` - y方向グリッド間隔
- `config.nz` - z方向グリッド数（通常74）
- `config.vgrid_filepath` - 鉛直グリッドファイルパス

### 時間範囲
- `config.t_first` - 開始時刻インデックス
- `config.t_last` - 終了時刻インデックス
- `config.time_list` - 時刻のリスト（hour単位）

### 中心座標
- `config.center_x` - x方向中心座標リスト
- `config.center_y` - y方向中心座標リスト

---

## 今後の作業候補

### コード品質改善
- [ ] pylint スコアの継続的改善
- [ ] 型ヒントの追加
- [ ] docstring の充実

### 機能追加
- [ ] エラーハンドリングの強化
- [ ] ログ出力機能の追加
- [ ] プログレスバーの追加

### テスト
- [ ] ユニットテストの作成
- [ ] データサイズ一貫性チェックの自動化
- [ ] パス生成のテスト

---

## メモ

- Claude Code は会話の記憶が保持されないため、このログファイルを次回セッションの冒頭で読み込むこと
- 新しい修正を行った際は、このログファイルを更新すること
- 重要な決定事項や注意点は「重要な注意事項」セクションに追記すること

---

## 変更履歴

### 2025-11-28
- ディレクトリ再編成の完了
- 新しいパスメソッドの追加（`get_domain_path`, `get_center_path`, `get_tc_centric_path`）
- 全170ファイルのマイグレーション
- `utils/vorticity.py` の作成と渦度計算の共通化
- 流線関数プロットのオンデマンド化
- vertical/profileのパス修正
- WORK_LOG.md の作成

### 2025-11-13
- グリッド生成の統一化を実施
- ビニング方法の統一化を実施
- azim_mean/, azim_mean/eliassen/, azim_mean/eq_momentum_u/, azim_q8/ の修正完了
- sums/ の修正完了 (setting.json → AnalysisConfig に移行)
- symmetrisity/ の修正完了 (IndexError修正、GridHandler使用、グリッド生成統一)
- z_profile_q4/ の修正完了 (Fortran .dat → numpy .npy に移行、GridHandler使用)
- utils/grid.py に nz パラメータを追加
