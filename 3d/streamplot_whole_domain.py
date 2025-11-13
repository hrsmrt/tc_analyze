"""
streamplot_whole_domain

解析処理を実行します。
"""

# python $WORK/tc_analyze/3d/streamplot_whole_domain.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

R_MAX = 1000e3

# 格子点座標（m単位）
x = (np.arange(config.nx) + 0.5) * config.dx
y = (np.arange(config.ny) + 0.5) * config.dy
grid.X, grid.Y = np.meshgrid(x, y)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]

FOLDER = "./fig/3d/whole_domain/streamplot/"
os.makedirs(FOLDER, exist_ok=True)

for z in z_list:
    os.makedirs(f"./fig/3d/whole_domain/streamplot/z{str(z).zfill(2)}", exist_ok=True)

data_all_u = np.memmap(
    f"{config.input_folder}/ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_all_v = np.memmap(
    f"{config.input_folder}/ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    data_u = data_all_u[t]  # shape: (config.nz, config.ny, config.nx)
    data_v = data_all_v[t]  # shape: (config.nz, config.ny, config.nx)
    for z in z_list:
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.streamplot(grid.X, grid.Y, data_u[z], data_v[z])
        ax.set_title(f"t={t * config.dt_hour}h z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        fig.savefig(
            f"./fig/3d/whole_domain/streamplot/z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"
        )
        plt.close()
    print(f"t: {t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last, int(24 / config.dt_hour))
)
