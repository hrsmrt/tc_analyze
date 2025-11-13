"""

config = AnalysisConfig()
grid = GridHandler(config)

python $WORK/tc_analyze/azim_mean/azim_tb_tangential_plot.py $style
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

# グリッド設定：データから実際のビン数を取得
sample_data = np.load(f"./data/azim/tb_tangential/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

folder = "./fig/azim/tb_tangential/"

os.makedirs(folder, exist_ok=True)


def process_t(t):
    data = np.load(f"./data/azim/tb_tangential/t{str(t).zfill(3)}.npy")

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(r_mesh, z_mesh, data, cmap="bwr", levels=np.linspace(-0.01, 0.01, 21))
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_ticks([-0.01, 0, 0.01])
    ax.set_title(f"方位角平均 tb d接線風 t = {config.time_list[t]} hour")
    set_azimuthal_plot_ticks(ax, r_max=R_MAX, z_max=20e3)
    # ax.set_xlabel("半径 [km]")
    # ax.set_ylabel("高度 [km]")
    # plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(config.dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
    plt.savefig(f"{folder}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
