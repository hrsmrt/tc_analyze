"""
相当温位の方位角平均プロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

python $WORK/tc_analyze/azim_mean/azim_theta_e_plot.py $style
"""

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_theta_e
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

OUTPUT_FOLDER = config.get_tc_centric_path("azimuthal", "basic/theta_e", data_type="fig")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く
data_tem = np.memmap(
    f"{config.input_folder}ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_pres = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_qv = np.memmap(
    f"{config.input_folder}ms_qv.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    theta_e_data = calculate_azimuthal_mean_theta_e(
        data_tem, data_pres, data_qv, t, center_x_list, center_y_list, grid
    )

    # グリッド設定：データから実際のビン数を取得
    nr = theta_e_data.shape[1]
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
        theta_e_data,
        levels=np.arange(330, 375, 5),
        cmap="rainbow",
        extend="both",
    )
    colorbar = fig.colorbar(contour_filled, ax=ax)
    colorbar.set_ticks([330, 370])
    ax.set_ylim([0, 20])
    ax.set_title(f"相当温位 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.png"))
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
