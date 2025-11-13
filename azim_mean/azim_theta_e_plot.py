# python $WORK/tc_analyze/azim_mean/azim_theta_e_plot.py $style

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
sample_data = np.load(f"./data/azim/theta_e/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

# km単位に変換
r_mesh_km = r_mesh * 1e-3
z_mesh_km = z_mesh * 1e-3

OUTPUT_FOLDER = "./fig/azim/theta_e/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_t(t):
    theta_e_data = np.load(f"./data/azim/theta_e/t{str(t).zfill(3)}.npy")

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    contour_filled = ax.contourf(
        r_mesh_km,
        z_mesh_km,
        theta_e_data,
        levels=np.arange(330, 375, 5),
        cmap="rainbow",
        extend="both",
    )
    colorbar = fig.colorbar(contour_filled, ax=ax)
    colorbar.set_ticks([330, 370])
    ax.set_ylim([0, 20])
    ax.set_title(f"相当温位 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{OUTPUT_FOLDER}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
