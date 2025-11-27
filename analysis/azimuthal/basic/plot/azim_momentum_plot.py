"""
角運動量の方位角平均プロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

python $WORK/tc_analyze/azim_mean/azim_momentum_plot.py $style
"""

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_momentum, calculate_azimuthal_mean_wind
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

OUTPUT_FOLDER = config.get_fig_path("azim", "momentum")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く
data_u = np.memmap(
    f"{config.input_folder}ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_v = np.memmap(
    f"{config.input_folder}ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    # まず接線風の方位角平均を計算
    _, azim_tangential = calculate_azimuthal_mean_wind(
        data_u, data_v, t, center_x_list, center_y_list, grid
    )
    # 接線風から角運動量を計算
    momentum_data = calculate_azimuthal_mean_momentum(azim_tangential, config)

    # グリッド設定：データから実際のビン数を取得
    nr = momentum_data.shape[1]
    R_MAX = nr * config.dx
    r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

    # km単位に変換
    r_mesh_km = r_mesh * 1e-3
    z_mesh_km = z_mesh * 1e-3

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    contour_filled = ax.contourf(
        r_mesh_km,
        z_mesh_km,
        momentum_data,
        levels=np.arange(0, 2.8e7, 0.4e7),
        cmap="rainbow",
        extend="both",
    )
    colorbar = fig.colorbar(contour_filled, ax=ax)
    colorbar.set_ticks([0, 2.8e7])
    ax.set_ylim([0, 20])
    ax.set_title(f"角運動量 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.png"))
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
