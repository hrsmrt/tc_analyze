"""
whole_domain

解析処理を実行します。
"""

# python $WORK/tc_analyze/3d/whole_domain.py varname $style
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

VARNAME = sys.argv[1]

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

os.makedirs(str(f"./fig/3d/whole_domain/{VARNAME}"), exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(f"./fig/3d/whole_domain/{VARNAME}/z{str(z).zfill(2)}", exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

x_axis = np.arange(0.5 * config.dx, config.nx * config.dx, config.dx)
y_axis = np.arange(0.5 * config.dy, config.ny * config.dy, config.dy)
grid.X, grid.Y = np.meshgrid(x_axis, y_axis)

data_memmap = np.memmap(
    f"{config.input_folder}{VARNAME}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    for z in z_list:
        data = data_memmap[t, z, :, :]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 4))
        match VARNAME:
            case "ms_u":
                c = ax.contourf(
                    grid.X,
                    grid.Y,
                    data,
                    levels=np.arange(-40, 45, 5),
                    cmap="bwr",
                    extend="both",
                )
            case "ms_v":
                c = ax.contourf(
                    grid.X,
                    grid.Y,
                    data,
                    levels=np.arange(-40, 45, 5),
                    cmap="bwr",
                    extend="both",
                )
            case "ms_w":
                c = ax.contourf(
                    grid.X,
                    grid.Y,
                    data,
                    levels=np.arange(-4, 4.5, 0.5),
                    cmap="bwr",
                    extend="both",
                )
            case "ms_tem":
                if z == 0:
                    c = ax.contourf(
                        grid.X,
                        grid.Y,
                        data,
                        levels=np.arange(295, 305, 1),
                        cmap="rainbow",
                        extend="both",
                    )
                else:
                    c = ax.contourf(grid.X, grid.Y, data, cmap="rainbow", extend="both")
            case "ms_rh":
                c = ax.contourf(
                    grid.X,
                    grid.Y,
                    data,
                    levels=np.arange(0, 1.2, 0.1),
                    cmap="rainbow",
                    extend="both",
                )
            case "ms_qv":
                if z == 0:
                    c = ax.contourf(
                        grid.X,
                        grid.Y,
                        data,
                        levels=np.arange(0.005, 0.027, 0.002),
                        cmap="rainbow",
                        extend="both",
                    )
                else:
                    c = ax.contourf(grid.X, grid.Y, data, cmap="rainbow", extend="both")
            case _:
                c = ax.contourf(grid.X, grid.Y, data, cmap="rainbow")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(
            "right", size="5%", pad=0.1
        )  # size: colorbar幅, pad: 図との距離
        fig.colorbar(c, cax=cax)
        ax.set_title(f"t={config.time_list[t]:3d}h,z={int(vgrid[z] * 1e-2) * 1e-1}km")
        ax.set_xticks(
            [0, config.x_width / 2, config.x_width],
            ["", "", ""],
        )
        ax.set_yticks(
            [0, config.y_width / 2, config.y_width],
            ["", "", ""],
        )
        # ax.set_xlabel("x [km]")
        # ax.set_ylabel("y [km]")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        fig.savefig(
            f"./fig/3d/whole_domain/{VARNAME}/z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last, int(24 / config.dt_hour))
)
