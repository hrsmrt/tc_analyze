# python $WORK/tc_analyze/azim_mean/azim_stream_plot.py $style

import os
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument(arg_index=1)

r_max = 1000e3

X, Y = grid.create_radial_vertical_meshgrid(r_max)

output_folder = "./fig/azim/stream/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/stream/t{str(t).zfill(3)}.npy")
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    c = ax.contour(X*1e-3, Y*1e-3, data,levels = np.arange(0, 1e10, 5e8), cmap="rainbow", extend="both")
    cbar = fig.colorbar(c,ax=ax)
    #cbar.set_ticks([330,370])
    ax.set_ylim([0,20e3])
    ax.set_title(f"流線関数 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
