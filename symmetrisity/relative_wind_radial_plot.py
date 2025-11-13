# python $WORK/tc_analyze/symmetrisity/relative_wind_radial_plot.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()
grid = GridHandler(config)

# グリッド設定：データから実際のサイズを取得
sample_data = np.load(
    f"./data/symmetrisity/relative_wind_radial/t{str(config.t_first).zfill(3)}.npy"
)
nr = sample_data.shape[1]
R_MAX = nr * config.dx
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

output_folder = "./fig/symmetrisity/relative_wind_radial/"

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # データの読み込み
    data = np.load(f"./data/symmetrisity/relative_wind_radial/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(
        r_mesh * 1e-3,
        z_mesh * 1e-3,
        data,
        cmap="Reds_r",
        levels=np.arange(0, 1.1, 0.1),
        extend="both",
    )
    fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20])
    ax.set_title(f"軸対称性 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")

    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
