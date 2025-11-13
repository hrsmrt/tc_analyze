"""
psi_r200 のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/3d/psi_plot_r200.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_empty

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 200e3

center_x_list = config.center_x
center_y_list = config.center_y

OUTPUT_FOLDER = "./fig/3d/psi/r200/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(f"{OUTPUT_FOLDER}z{str(z).zfill(2)}", exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")


def process_t(t):
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    data_t = np.load(f"./data/3d/psi/psi_t{str(t).zfill(3)}.npy")
    for z in z_list:
        data = data_t[z, :, :]
        data_cut = grid.extract_vortex_region(data, center_x, center_y, EXTENT)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        c = ax.contour(X_cut, Y_cut, data_cut)
        fig.colorbar(c, ax=ax)
        set_vortex_region_ticks_empty(ax, EXTENT)
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(
            f"{OUTPUT_FOLDER}z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png"
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last, int(24 / config.dt_hour))
)
