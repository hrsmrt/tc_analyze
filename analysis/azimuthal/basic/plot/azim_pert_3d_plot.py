# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_pert_3d_plot.py varname $style
# 方位角平均データから環境場平均（r>1000km）を引いてプロット
import os
import sys

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

varname = sys.argv[1]

mpl_style_sheet = parse_style_argument()
config = AnalysisConfig()
grid = GridHandler(config)

time_list = config.time_list

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

r_max = 1000e3
nr = int(np.floor(r_max / config.dx))
xgrid = np.arange(nr) * config.dx * 1e-3

X, Y = np.meshgrid(xgrid, vgrid * 1e-3)

# Output directory
folder = config.get_tc_centric_path("azimuthal", f"basic/pert/{varname}", data_type="fig")
os.makedirs(folder, exist_ok=True)

# Load 3D data for calculating environmental mean (r > r_max)
data_all = np.memmap(
    f"{config.input_folder}{varname}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)

# Center coordinates
center_x_list = config.center_x
center_y_list = config.center_y

# Pre-calculate grid
X_grid, Y_grid = grid.X, grid.Y


def process_t(t):
    # Load azimuthal mean data from basic/{varname} (.npz優先、.npyフォールバック)
    data_path = config.get_tc_centric_path('azimuthal', f'basic/{varname}')
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        azim_mean = npz_data['data']
    elif os.path.exists(npy_path):
        azim_mean = np.load(npy_path)  # 旧形式フォールバック
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

    # Calculate environmental mean (r > r_max)
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X_grid - cx) ** 2 + (Y_grid - cy) ** 2)
    mask_outside = R > r_max

    data_3d = data_all[t]
    masked_data = np.where(mask_outside, data_3d, np.nan)
    mean_outside = np.nanmean(masked_data, axis=(1, 2))  # (nz,)

    # Calculate perturbation: azim_mean - environmental_mean
    data = azim_mean - mean_outside[:, np.newaxis]

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    title_name = varname
    match varname:
        case "ms_tem":
            c = ax.contourf(
                X, Y, data, levels=np.arange(-10, 12, 2), cmap="bwr", extend="both"
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-10, 0, 10])
            title_name = "気温偏差"
        case "ms_pres":
            c = ax.contourf(
                X,
                Y,
                data * 1e-2,
                levels=np.arange(-100, 1, 10),
                cmap="rainbow_r",
                extend="both",
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-100, 0])
            title_name = "気圧偏差"
        case "ms_rho":
            c = ax.contourf(
                X,
                Y,
                data,
                levels=np.arange(-0.1, 0.11, 0.01),
                cmap="bwr_r",
                extend="both",
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-0.1, 0, 0.1])
            title_name = "密度偏差"
        case _:
            c = ax.contourf(X, Y, data, cmap="rainbow", extend="both")
            fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20])
    ax.set_xticks([0, 250, 500, 750, 1000], [0, "", "", "", 1000])
    ax.set_yticks([0, 5, 10, 15, 20], [0, "", "", "", 20])
    ax.set_title(f"方位角平均 {title_name} t = {time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")

    fig.savefig(os.path.join(folder, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
