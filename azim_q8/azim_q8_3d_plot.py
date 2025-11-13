# python $WORK/tc_analyze/azim_q8/azim_q8_3d_plot.py varname $style
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

varname = sys.argv[1]
mpl_style_sheet = parse_style_argument()

# グリッド設定：データから実際のサイズを取得
sample_data = np.load(f"./data/azim_q8/{varname}/t{str(config.t_first).zfill(3)}.npy")
nz_data, nr, n_sectors = sample_data.shape
R_MAX = nr * config.dx

# rgrid と vgrid を作成
rgrid = (np.arange(nr) + 0.5) * config.dx * 1e-3  # km単位
vgrid = grid.create_vertical_grid() * 1e-3  # km単位

X, Y = np.meshgrid(rgrid, vgrid)

folder = f"./fig/azim_q8/{varname}/"

os.makedirs(folder, exist_ok=True)

sector_names = [f"sector{s}" for s in range(8)]


def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim_q8/{varname}/t{str(t).zfill(3)}.npy")

    # 各sectorごとにプロット
    for s in range(8):
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 2))
        data_s = data[:, :, s]
        match varname:
            case "ms_u":
                c = ax.contourf(
                    X,
                    Y,
                    data_s,
                    levels=np.arange(-40, 45, 5),
                    cmap="bwr",
                    extend="both",
                )
                cb = fig.colorbar(c, ax=ax)
                cb.set_ticks([-40, 0, 45])
            case "ms_v":
                c = ax.contourf(
                    X,
                    Y,
                    data_s,
                    levels=np.arange(-40, 45, 5),
                    cmap="bwr",
                    extend="both",
                )
                cb = fig.colorbar(c, ax=ax)
                cb.set_ticks([-40, 0, 45])
            case "ms_w":
                c = ax.contourf(
                    X,
                    Y,
                    data_s,
                    levels=np.arange(-1, 1.1, 0.1),
                    cmap="bwr",
                    extend="both",
                )
                cb = fig.colorbar(c, ax=ax)
                cb.set_ticks([-1, 0, 1])
            case "ms_rh":
                c = ax.contourf(
                    X,
                    Y,
                    data_s,
                    levels=np.arange(0, 1.2, 0.1),
                    cmap="rainbow",
                    extend="max",
                )
                cb = fig.colorbar(c, ax=ax)
                cb.set_ticks([0, 1.0])
            case "ms_dh":
                c = ax.contourf(
                    X,
                    Y,
                    data_s,
                    levels=np.arange(0, 0.001, 0.0001),
                    cmap="rainbow",
                    extend="max",
                )
                cb = fig.colorbar(c, ax=ax)
                cb.set_ticks([0, 0.001])
            case _:
                c = ax.contourf(X, Y, data_s, cmap="rainbow", extend="both")
                fig.colorbar(c, ax=ax)
        ax.set_ylim([0, 20])
        ax.set_title(f"{sector_names[s]} {varname} t = {config.time_list[t]} hour")
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("高度 [km]")

        sec_folder = os.path.join(folder, sector_names[s])
        os.makedirs(sec_folder, exist_ok=True)
        fig.savefig(f"{sec_folder}/t{str(t).zfill(3)}.png")
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
