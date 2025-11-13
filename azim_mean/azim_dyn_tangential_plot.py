"""

config = AnalysisConfig()
grid = GridHandler(config)

python $WORK/tc_analyze/azim_mean/azim_dyn_tangential_plot.py $style
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_azimuthal_plot_ticks

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

radius = 1000e3

nr = int(radius / config.dx)

vgrid = grid.create_vertical_grid()
# rgrid generated via grid.create_radial_vertical_meshgrid

X, Y = grid.create_radial_vertical_meshgrid(1000e3)

folder = "./fig/azim/dyn_tangential/"

os.makedirs(folder, exist_ok=True)


def process_t(t):
    data = np.load(f"./data/azim/dyn_tangential/t{str(t).zfill(3)}.npy")

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(X, Y, data, cmap="bwr", levels=np.linspace(-0.01, 0.01, 21))
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_ticks([-0.01, 0, 0.01])
    ax.set_title(f"方位角平均 dyn d接線風 t = {config.time_list[t]} hour")
    set_azimuthal_plot_ticks(ax, r_max=1000e3, z_max=20e3)
    # ax.set_xlabel("半径 [km]")
    # ax.set_ylabel("高度 [km]")
    plt.savefig(f"{folder}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
