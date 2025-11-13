# python $WORK/tc_analyze/azim_mean/azim_wind_relative_radial_plot.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

# グリッド設定：データから実際のビン数を取得
sample_data = np.load(f"./data/azim/wind_relative_radial/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

OUTPUT_FOLDER = "./fig/azim/wind_relative_radial/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_t(t):
    radial_wind_data = np.load(
        f"./data/azim/wind_relative_radial/t{str(t).zfill(3)}.npy"
    )

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
    plt.savefig(f"{OUTPUT_FOLDER}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
