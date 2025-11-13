# python $WORK/tc_analyze/azim_mean/azim_wind_tangential_r_v.py $style
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
sample_data = np.load(f"./data/azim/wind_tangential/t{str(config.t_first).zfill(3)}.npy")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
rgrid = grid.create_radial_grid(R_MAX)
vgrid = grid.create_vertical_grid()

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]

folder = "./fig/azim/wind_tangential/"

os.makedirs(folder, exist_ok=True)
for z in z_list:
    os.makedirs(f"{folder}z{str(z).zfill(2)}", exist_ok=True)


def process_t(t):
    data = np.load(f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy")
    for z in z_list:
        folder_z = f"{folder}z{str(z).zfill(2)}/"
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.plot(rgrid, data[z])
        ax.set_title(
            f"方位角平均接線風 t = {config.time_list[t]} hour, z = {vgrid[z]:.1f} km"
        )
        ax.set_ylim([0, 50e3])
        ax.set_yticks([0, 10e3, 20e3, 30e3, 40e3, 50e3])
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("風速 [m/s]")
        plt.savefig(f"{folder_z}t{str(t).zfill(3)}.png")
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
