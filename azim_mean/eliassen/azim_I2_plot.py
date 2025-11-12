# python $WORK/tc_analyze/azim_mean/eliassen/azim_I2_plot.py $style
# I2のi+1/2上の値

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

output_folder = "./fig/azim/eliassen/I2/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/eliassen/I2/t{str(t).zfill(3)}.npy")
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    c = ax.contourf(X*1e-3, Y*1e-3, data, cmap="rainbow", extend="both")
    cbar = fig.colorbar(c,ax=ax)
    #cbar.set_ticks([300,400])
    ax.set_ylim([0,20])
    ax.set_title(f"B t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done(max:{data.max()},min:{data.min()})")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
