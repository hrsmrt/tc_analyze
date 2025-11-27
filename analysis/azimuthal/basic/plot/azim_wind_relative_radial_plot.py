"""
相対風の方位角平均動径風のプロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

python $WORK/tc_analyze/azim_mean/azim_wind_relative_radial_plot.py $style
"""
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_relative_wind
from utils.basic import calculate_center_velocity
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

OUTPUT_FOLDER = config.get_fig_path("azim", "wind_relative_radial")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# 台風中心の移動速度を計算
center_u_list, center_v_list = calculate_center_velocity(
    center_x_list, center_y_list, config.dt_output
)

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
    radial_wind_data, _ = calculate_azimuthal_mean_relative_wind(
        data_u, data_v, t, center_x_list, center_y_list, center_u_list, center_v_list, grid
    )

    # グリッド設定：データから実際のビン数を取得
    nr = radial_wind_data.shape[1]
    R_MAX = nr * config.dx
    r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    contour_filled = ax.contourf(
        r_mesh,
        z_mesh,
        radial_wind_data,
        cmap="bwr",
        levels=np.arange(-15, 16, 3),
        extend="both",
    )
    colorbar = fig.colorbar(contour_filled, ax=ax)
    colorbar.set_ticks([-15, 0, 15])
    ax.set_title(f"方位角平均動径風 t = {config.time_list[t]} hour")
    ax.set_ylim([0, 20e3])
    ax.set_xticks([0, 250e3, 500e3, 750e3, 1000e3], ["", "", "", "", ""])
    ax.set_yticks([0, 5e3, 10e3, 15e3, 20e3], ["", "", "", "", ""])
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    plt.savefig(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
