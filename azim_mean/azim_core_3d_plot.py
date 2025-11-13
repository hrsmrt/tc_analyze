# python $WORK/tc_analyze/azim_mean/azim_core_3d_plot.py varname $style
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

VARNAME = sys.argv[1]

mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()
grid = GridHandler(config)

time_list = config.time_list

R_MAX = 1000e3

r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

OUTPUT_FOLDER = f"./fig/azim_core/{VARNAME}/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim/{VARNAME}/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    title_name = VARNAME
    match VARNAME:
        case "ms_u":
            contour = ax.contourf(
                r_mesh,
                z_mesh,
                data,
                levels=np.arange(-40, 45, 5),
                cmap="bwr",
                extend="both",
            )
            colorbar = fig.colorbar(contour, ax=ax)
            colorbar.set_ticks([-40, 0, 45])
        case "ms_v":
            contour = ax.contourf(
                r_mesh,
                z_mesh,
                data,
                levels=np.arange(-40, 45, 5),
                cmap="bwr",
                extend="both",
            )
            colorbar = fig.colorbar(contour, ax=ax)
            colorbar.set_ticks([-40, 0, 45])
        case "ms_w":
            contour = ax.contourf(
                r_mesh,
                z_mesh,
                data,
                levels=np.arange(-1, 1.1, 0.1),
                cmap="bwr",
                extend="both",
            )
            colorbar = fig.colorbar(contour, ax=ax)
            colorbar.set_ticks([-1, 0, 1])
            title_name = "鉛直風"
        case "ms_rh":
            contour = ax.contourf(
                r_mesh,
                z_mesh,
                data,
                levels=np.arange(0, 1.2, 0.1),
                cmap="rainbow",
                extend="max",
            )
            colorbar = fig.colorbar(contour, ax=ax)
            colorbar.set_ticks([0, 1.0])
        case "ms_dh":
            contour = ax.contourf(
                r_mesh,
                z_mesh,
                data,
                levels=np.arange(0, 0.001, 0.0001),
                cmap="rainbow",
                extend="max",
            )
            colorbar = fig.colorbar(contour, ax=ax)
            colorbar.set_ticks([0, 0.001])
        case _:
            contour = ax.contourf(
                r_mesh, z_mesh, data, cmap="rainbow", extend="both"
            )
            fig.colorbar(contour, ax=ax)
    ax.set_ylim([0, 20e3])
    ax.set_xlim([0, 150e3])
    ax.set_xticks([0, 50e3, 100e3, 150e3], [0, "", "", 150])
    ax.set_yticks([0, 5e3, 10e3, 15e3, 20e3], [0, "", "", "", 20])
    ax.set_aspect("equal", "box")
    ax.set_title(f"方位角平均 {title_name} t = {time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")

    fig.savefig(f"{OUTPUT_FOLDER}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
