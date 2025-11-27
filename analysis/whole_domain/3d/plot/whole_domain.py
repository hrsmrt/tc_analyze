"""Plot 3D data over whole domain."""
# python $WORK/tc_analyze/3d/whole_domain.py varname $style
import os
import sys

import matplotlib
matplotlib.use('Agg')  # ✅ 高速化: GUI描画のオーバーヘッド削減
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

OUTPUT_DIR = config.get_fig_path("3d", "whole_domain", VARNAME)
os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

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

# ✅ 高速化: levelsを事前計算（毎回np.arange()を呼ばないように）
LEVELS_U_V = np.arange(-40, 45, 5)
LEVELS_W = np.arange(-4, 4.5, 0.5)
LEVELS_TEM_Z0 = np.arange(295, 305, 1)
LEVELS_RH = np.arange(0, 1.2, 0.1)
LEVELS_QV_Z0 = np.arange(0.005, 0.027, 0.002)


def process_t_z(t, z):
    """✅ 高速化: (t,z)ペアで並列化（より細かい粒度）"""
    data = data_memmap[t, z, :, :]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 4))

    match VARNAME:
        case "ms_u":
            c = ax.contourf(
                grid.X,
                grid.Y,
                data,
                levels=LEVELS_U_V,
                cmap="bwr",
                extend="both",
            )
        case "ms_v":
            c = ax.contourf(
                grid.X,
                grid.Y,
                data,
                levels=LEVELS_U_V,
                cmap="bwr",
                extend="both",
            )
        case "ms_w":
            c = ax.contourf(
                grid.X,
                grid.Y,
                data,
                levels=LEVELS_W,
                cmap="bwr",
                extend="both",
            )
        case "ms_tem":
            if z == 0:
                c = ax.contourf(
                    grid.X,
                    grid.Y,
                    data,
                    levels=LEVELS_TEM_Z0,
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
                levels=LEVELS_RH,
                cmap="rainbow",
                extend="both",
            )
        case "ms_qv":
            if z == 0:
                c = ax.contourf(
                    grid.X,
                    grid.Y,
                    data,
                    levels=LEVELS_QV_Z0,
                    cmap="rainbow",
                    extend="both",
                )
            else:
                c = ax.contourf(grid.X, grid.Y, data, cmap="rainbow", extend="both")
        case _:
            c = ax.contourf(grid.X, grid.Y, data, cmap="rainbow")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(c, cax=cax)
    ax.set_title(f"t={config.time_list[t]:3d}h,z={vgrid[z] * 1e-3:.1f}km")
    ax.set_xticks([0, config.x_width / 2, config.x_width], ["", "", ""])
    ax.set_yticks([0, config.y_width / 2, config.y_width], ["", "", ""])
    ax.grid(False)
    ax.set_aspect("equal", "box")
    fig.savefig(
        os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}", f"t{str(t).zfill(3)}.png")
    )
    plt.close()
    print(f"t={t}, z={z} done")


# ✅ 高速化: (t, z)のペアで並列化（より多くの並列度）
Parallel(n_jobs=config.n_jobs)(
    delayed(process_t_z)(t, z)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
    for z in z_list
)

print(f"✅ 完了: {OUTPUT_DIR}")
