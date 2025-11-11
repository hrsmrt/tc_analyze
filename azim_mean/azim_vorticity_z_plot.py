# python $WORK/tc_analyze/azim_mean/azim_vorticity_z_plot.py $style

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

vgrid = np.loadtxt(config.vgrid_filepath)

output_folder = "./fig/azim/vorticity_z/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/vorticity_z/t{str(t).zfill(3)}.npy")
    # データの形状から半径方向のグリッドを作成
    nr = data.shape[1]
    xgrid = np.arange(nr) * config.dx
    X, Y = np.meshgrid(xgrid, vgrid)
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    c = ax.contourf(X, Y, data,levels=np.arange(-0.001,0.0011,0.0001), cmap="bwr", extend="both")
    cbar = fig.colorbar(c,ax=ax)
    ax.set_ylim([0,20e3])
    ax.set_title(f"渦度 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
