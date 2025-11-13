# python $WORK/tc_analyze/symmetrisity/relative_wind_tangential_plot.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()

# ファイルを開いてJSONを読み込む

config = AnalysisConfig()
grid = GridHandler(config)

X, Y = np.meshgrid(grid.xgrid, grid.vgrid)

output_folder = f"./fig/symmetrisity/relative_wind_tangential/"

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # データの読み込み
    data = np.load(
        f"./data/symmetrisity/relative_wind_tangential/t{str(t).zfill(3)}.npy"
    )

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(
        X, Y, data, cmap="Reds_r", levels=np.arange(0, 1.1, 0.1), extend="both"
    )
    fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20e3])
    ax.set_title(f"軸対称性 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")

    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
