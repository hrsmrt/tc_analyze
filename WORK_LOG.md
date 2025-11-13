# tc_analyze プロジェクト作業ログ

## 最終更新日: 2025-11-13

---

## 実施した主な変更

### 1. グリッド生成の統一化

#### utils/grid.py の拡張
- `create_radial_vertical_meshgrid(r_max, nz=None)` に `nz` パラメータを追加
- z方向のグリッド数を指定可能にし、微分後のデータ（nz-1）に対応

```python
def create_radial_vertical_meshgrid(
    self, r_max: float, nz: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    rgrid = self.create_radial_grid(r_max)
    vgrid = self.create_vertical_grid()
    if nz is not None:
        vgrid = vgrid[:nz]
    return np.meshgrid(rgrid, vgrid)
```

#### プロットファイルの統一パターン

**基本パターン（方位角平均データ）:**
```python
# グリッド設定：データから実際のビン数を取得
sample_data = np.load(f"./data/azim/XXX/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)
```

**z方向微分データの場合（例: N2）:**
```python
sample_data = np.load(f"./data/azim/eliassen/N2/t{str(config.t_first).zfill(3)}.npy")
nz_data, nr = sample_data.shape
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX, nz=nz_data)
```

**eq_momentum_u の特殊パターン（shifted cell center）:**
```python
sample_data = np.load(f"./data/azim/eq_momentum_u/grad_p/t{str(config.t_first).zfill(3)}.npy")
nz_data, nr_data = sample_data.shape
vgrid = grid.create_vertical_grid()[:nz_data] * 1e-3
rgrid_wall = ((np.arange(nr_data) + 1) * config.dx + config.dx / 2) * 1e-3
X, Y = np.meshgrid(rgrid_wall, vgrid)
```

### 2. ビニング方法の統一化

#### 計算ファイルの統一パターン
```python
# 統一されたビニング方法
bin_idx = np.floor(valid_r / config.dx).astype(int)
max_bin = int(np.floor(r_max / config.dx))
bin_idx = np.clip(bin_idx, 0, max_bin - 1)
count_r = np.bincount(bin_idx, minlength=max_bin)
azim_sum = np.zeros((config.nz, max_bin))
```

**重要:** `//` 演算子ではなく `np.floor()` を使用することで、データサイズの一貫性を保証

### 3. 修正したファイル一覧

#### azim_mean/ (26ファイル)
**プロットファイル (16):**
- azim_momentum_plot.py
- azim_theta_e_plot.py
- azim_plot_momentum_theta_e.py (特殊: 2つのデータセットを扱う)
- azim_wind_relative_radial_plot.py
- azim_wind_relative_tangential_plot.py
- azim_dyn_radial_plot.py, azim_dyn_tangential_plot.py
- azim_mp_radial_plot.py, azim_mp_tangential_plot.py
- azim_phy_radial_plot.py, azim_phy_tangential_plot.py
- azim_tb_radial_plot.py, azim_tb_tangential_plot.py
- azim_wind_radial_plot2.py
- azim_wind_tangential_r_v.py
- azim_wind_relative_tangential_max_z_plot.py

**計算ファイル (10):**
- azim_wind_calc.py
- azim_2d_calc.py
- azim_dyn_calc.py
- azim_mp_calc.py
- azim_phy_calc.py
- azim_tb_calc.py
- azim_vorticity_z_calc.py
- azim_wind_calc2.py
- azim_wind_relative_calc.py
- azim_wind10m_calc.py

#### azim_mean/eliassen/ (10ファイル)
**プロットファイル (8):**
- azim_N2_plot.py (z方向微分データ、nz-1のサイズ)
- azim_I2_plot.py
- azim_I_prime2_plot.py
- azim_B_plot.py
- azim_R_plot.py
- azim_gamma_plot.py
- azim_xi_plot.py
- azim_buoyancy_plot.py

**計算ファイル (2):**
- azim_I2_calc.py
- azim_I_prime2_calc.py
- azim_N2_calc.py (修正: `int(np.floor(r_max / config.dx))`)

#### azim_mean/eq_momentum_u/ (5ファイル)
- azim_du_dr_plot.py (cell wall座標)
- azim_udu_dr_plot.py (cell wall座標)
- azim_grad_p_plot.py (shifted cell center)
- azim_gradient_wind_eq_plot.py (shifted cell center)
- azim_gradient_balance_score_plot.py (shifted cell center)

#### azim_q8/ (5ファイル)
**計算ファイル (2):**
- azim_q8_3d_calc.py (setting.json → AnalysisConfig に移行)
- azim_q8_wind_relative_calc.py (setting.json → AnalysisConfig に移行)

**プロットファイル (3):**
- azim_q8_3d_plot.py (データ形状: nz, nr, 8 sectors)
- azim_q8_wind_relative_radial_plot.py
- azim_q8_wind_relative_tangential_plot.py

#### sums/ (2ファイル)
- sums_calc.py (setting.json → AnalysisConfig に移行)
- sums_plot.py (setting.json → AnalysisConfig に移行、parse_style_argument を使用)

#### symmetrisity/ (6ファイル)
**計算ファイル (3):**
- 3d_calc.py (ビニング方法修正、GridHandler使用、IndexError修正)
- relative_wind_radial_calc.py (ビニング方法修正、GridHandler使用)
- relative_wind_tangential_calc.py (ビニング方法修正、GridHandler使用)

**プロットファイル (3):**
- 3d_plot.py (データから実際のサイズ取得、グリッド生成修正)
- relative_wind_radial_plot.py (データから実際のサイズ取得、グリッド生成修正)
- relative_wind_tangential_plot.py (データから実際のサイズ取得、グリッド生成修正)

#### z_profile_q4/ (2ファイル)
- zeta_calc.py (Fortran .dat → numpy .npy に移行、GridHandler使用)
- zeta_plot.py (GridHandler使用、parse_style_argument使用、軸スケール修正)

#### その他
- utils/grid.py (create_radial_vertical_meshgrid に nz パラメータ追加)
- z_profile/sounding_rh_from_qv.py (コード品質改善)

---

## 重要な注意事項

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

### 座標系の種類

1. **セルセンター (cell center)**: `(np.arange(nr) + 0.5) * config.dx`
   - 標準的な方位角平均データで使用

2. **セルウォール (cell wall)**: `np.arange(nr) * config.dx`
   - du_dr, udu_dr などで使用

3. **シフトセルセンター (shifted cell center)**: `((np.arange(nr) + 1) * config.dx + config.dx / 2)`
   - grad_p などで使用

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
sample_data = np.load(f"./data/path/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

output_folder = "./fig/path/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(f"./data/path/t{str(t).zfill(3)}.npy")
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(r_mesh * 1e-3, z_mesh * 1e-3, data, cmap="rainbow", extend="both")
    fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20])
    ax.set_title(f"タイトル t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
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
output_folder = "./data/path/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    # 中心座標を取得
    cx = config.center_x[t]
    cy = config.center_y[t]

    # 距離計算とビニング
    R = grid.calculate_radial_distance(cx, cy)
    mask = R <= r_max
    valid_r = R[mask]

    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    azim_sum = np.zeros((config.nz, max_bin))
    count_r = np.bincount(bin_idx, minlength=max_bin)

    # データ処理...

    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
```

---

## 既知の問題と解決済み問題

### ✅ 解決済み

1. **TypeError: Shapes of x and z do not match**
   - 原因: 理論的なグリッドサイズと実際のデータサイズの不一致
   - 解決: データから実際のサイズを取得するパターンに統一

2. **データサイズの不一致（calc ファイル間）**
   - 原因: `//` と `np.floor()` の違い、`minlength` の欠如
   - 解決: 全ての calc ファイルでビニング方法を統一

3. **N2 データの形状エラー**
   - 原因: z方向微分により nz-1 のサイズになる
   - 解決: `create_radial_vertical_meshgrid` に `nz` パラメータを追加

4. **azim_q8 での setting.json 依存**
   - 原因: AnalysisConfig を使っていなかった
   - 解決: AnalysisConfig に統一

5. **symmetrisity での IndexError: index is out of bounds**
   - 原因: `//` 演算子による不一致、azim_mean データとビンサイズの不一致
   - 解決: データから実際の max_bin を取得し、`np.floor()` と `np.clip()` を使用

---

## 今後の作業候補

### コード品質改善
- [ ] 他のフォルダ（2d/, 3d/, center/, z_profile など）の統一化
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

---

## 参考情報

### 重要なファイル
- `utils/config.py` - 設定管理
- `utils/grid.py` - グリッド生成
- `utils/plotting.py` - プロット関連ユーティリティ
- `utils/basic.py` - 物理定数と基本関数

### グリッド設定
- `config.dx` - x方向グリッド間隔
- `config.dy` - y方向グリッド間隔
- `config.nz` - z方向グリッド数（通常74）
- `config.vgrid_filepath` - 鉛直グリッドファイルパス

### 時間範囲
- `config.t_first` - 開始時刻インデックス
- `config.t_last` - 終了時刻インデックス
- `config.time_list` - 時刻のリスト（hour単位）

---

## 変更履歴

### 2025-11-13
- グリッド生成の統一化を実施
- ビニング方法の統一化を実施
- azim_mean/, azim_mean/eliassen/, azim_mean/eq_momentum_u/, azim_q8/ の修正完了
- sums/ の修正完了 (setting.json → AnalysisConfig に移行)
- symmetrisity/ の修正完了 (IndexError修正、GridHandler使用、グリッド生成統一)
- z_profile_q4/ の修正完了 (Fortran .dat → numpy .npy に移行、GridHandler使用)
- utils/grid.py に nz パラメータを追加
- このログファイルを作成

---

## メモ

- Claude Code は会話の記憶が保持されないため、このログファイルを次回セッションの冒頭で読み込むこと
- 新しい修正を行った際は、このログファイルを更新すること
- 重要な決定事項や注意点は「重要な注意事項」セクションに追記すること
