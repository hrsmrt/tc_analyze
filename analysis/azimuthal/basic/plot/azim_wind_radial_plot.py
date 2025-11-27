"""
方位角平均動径風のプロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

python $WORK/tc_analyze/azim_mean/azim_wind_radial_plot.py $style
"""
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_wind
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()
grid = GridHandler(config)

vgrid = grid.create_vertical_grid()

folder = config.get_fig_path("azim", "wind_radial")

os.makedirs(folder, exist_ok=True)

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
    azim_radial, _ = calculate_azimuthal_mean_wind(
        data_u, data_v, t, center_x_list, center_y_list, grid
    )
    # データの形状から半径方向のグリッドを作成
    nr = azim_radial.shape[1]
    rgrid = (np.arange(nr) + 0.5) * config.dx
    X, Y = np.meshgrid(rgrid, vgrid)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(X, Y, azim_radial, cmap="bwr", levels=np.arange(-30, 35, 5), extend="both")
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_ticks([-30, 0, 30])
    ax.set_title(f"方位角平均動径風 t = {config.time_list[t]} hour")
    from utils.plotting import set_azimuthal_plot_ticks

    set_azimuthal_plot_ticks(ax, r_max=1000e3, z_max=20e3)
    # ax.set_xlabel("半径 [km]")
    # ax.set_ylabel("高度 [km]")
    plt.savefig(os.path.join(folder, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
