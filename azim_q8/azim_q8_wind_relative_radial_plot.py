# python $WORK/tc_analyze/azim_q8/azim_q8_wind_relative_radial_plot.py $style
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

# グリッド設定：データから実際のサイズを取得
sample_data = np.load(
    f"./data/azim_q8/wind_relative_radial/t{str(config.t_first).zfill(3)}.npy"
)
nz_data, nr, n_sectors = sample_data.shape
R_MAX = nr * config.dx

# rgrid と vgrid を作成
rgrid = (np.arange(nr) + 0.5) * config.dx * 1e-3  # km単位
vgrid = grid.create_vertical_grid() * 1e-3  # km単位

X, Y = np.meshgrid(rgrid, vgrid)

folder = "./fig/azim_q8/wind_relative_radial/"

os.makedirs(folder, exist_ok=True)

sector_names = [f"sector{s}" for s in range(8)]


def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim_q8/wind_relative_radial/t{str(t).zfill(3)}.npy")

    # 各sectorごとにプロット
    for s in range(8):
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 2))
        data_s = data[:, :, s]
        if t < 96:
            c = ax.contourf(
                X, Y, data_s, cmap="bwr", levels=np.arange(-30, 35, 5), extend="both"
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-30, 0, 30])
        else:
            c = ax.contourf(
                X, Y, data_s, cmap="bwr", levels=np.arange(-60, 70, 10), extend="both"
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-60, 0, 60])
        ax.set_ylim([0, 20])
        ax.set_title(f"{sector_names[s]} 動径風速 t = {config.time_list[t]} hour")
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("高度 [km]")

        sec_folder = os.path.join(folder, sector_names[s])
        os.makedirs(sec_folder, exist_ok=True)
        fig.savefig(f"{sec_folder}/t{str(t).zfill(3)}.png")
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
