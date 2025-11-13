# python $WORK/tc_analyze/2d/ss_wind10m_abs_vortex_region2.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_km_empty

mpl_style_sheet = parse_style_argument()

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:20] = [1, 1, 1, 1]  # 下限の20色を白に設定
custom_cmap = ListedColormap(colors)

OUTPUT_DIR = "./fig/2d/vortex_region2/wind10m_abs/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 設定の初期化
config = AnalysisConfig()
grid = GridHandler(config)
EXTENT = 500e3

center_list = np.loadtxt("./data/low_2.txt", delimiter=",", skiprows=1)
center_x_list = center_list[:, 1] * config.dx
center_y_list = center_list[:, 2] * config.dy

# GridHandlerから切り出し領域のメッシュグリッドを取得
X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

ss_u10m = np.fromfile(f"{config.input_folder}ss_u10m.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)
ss_v10m = np.fromfile(f"{config.input_folder}ss_v10m.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)
data_abs = np.sqrt(ss_v10m**2 + ss_u10m**2)


def process_t(t):
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    data_t = data_abs[t]
    data_cut = grid.extract_vortex_region(data_t, center_x, center_y, EXTENT)
    R_plot_max = 500e3  # 500 km
    cx = X_cut.mean()  # グリッドの中心を近似
    cy = Y_cut.mean()

    # 半径距離
    R = np.sqrt((X_cut - cx) ** 2 + (Y_cut - cy) ** 2)

    # 半径 R 内だけプロットするマスク
    mask = R <= R_plot_max
    data_masked = np.where(mask, data_cut, np.nan)  # 外側は NaN に

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5, 2))
    c = ax.contourf(
        X_cut * 1e-3,
        Y_cut * 1e-3,
        data_masked,
        cmap=custom_cmap,
        levels=np.arange(0, 51, 5),
        extend="max",
    )
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(
        "right", size="5%", pad=0.1
    )  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    set_vortex_region_ticks_km_empty(ax, EXTENT)
    ax.set_title(f"10m風速 [m/s] t={t * config.dt_hour}h")
    # ax.set_xticks([0, extent_x * config.dx * 1e-3, 2 * extent_x * config.dx * 1e-3],[-int(extent_x * config.dx * 1e-3),0, int(extent_x * config.dx * 1e-3)])
    # ax.set_yticks([0, extent_y * config.dy * 1e-3, 2 * extent_y * config.dy * 1e-3],[-int(extent_y * config.dy * 1e-3),0, int(extent_y * config.dy * 1e-3)])
    # ax.set_xlabel("x [km]")
    # ax.set_ylabel("y [km]")

    ax.set_aspect("equal", "box")
    fig.savefig(f"{OUTPUT_DIR}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
