"""
ms_dyn_tangential のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/3d/ms_dyn_tangential_plot.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_km

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

OUTPUT_DIR = "./fig/3d/vortex_region/dyn_tangential"

os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(f"{OUTPUT_DIR}/z{str(z).zfill(2)}", exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")


def process_t(t):
    data_t = np.load(f"./data/3d/dyn_tangential/t{str(t).zfill(3)}.npy")
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data = data_t[z, :, :]
        data_cut = grid.extract_vortex_region(data, center_x, center_y, EXTENT)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        c = ax.contourf(
            X_cut,
            Y_cut,
            data_cut,
            cmap="bwr",
            levels=np.arange(-30, 35, 5),
            extend="both",
        )
        fig.colorbar(c, ax=ax)
        set_vortex_region_ticks_km(ax, EXTENT)
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")
        fig.savefig(
            f"{OUTPUT_DIR}/z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png"
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last, int(24 / config.dt_hour))
)
