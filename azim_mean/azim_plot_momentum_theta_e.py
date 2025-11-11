# python $WORK/tc_analyze/azim_mean/azim_plot_momentum_theta_e.py $style

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

r_max = 1000e3

nr = int(r_max / config.dx)
R = (np.arange(nr) + 0.5) * config.dx * 1e-3
f = 3.77468e-5

vgrid = np.loadtxt(config.vgrid_filepath)
vgrid = vgrid * 1e-3

X, Y = np.meshgrid(R, vgrid)

output_folder = "./fig/azim/momentum_theta_e/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    data = np.load(f"./data/azim/momentum/t{str(t).zfill(3)}.npy")
    c = ax.contourf(X, Y, data,extend="max", levels=np.arange(0,2.8e7,2e6))
    fig.colorbar(c,ax=ax)
    data = np.load(f"./data/azim/theta_e/t{str(t).zfill(3)}.npy")
    ax.contour(X, Y, data, levels=np.arange(330,375,5), colors="black", linewidths=0.5)
    ax.set_ylim([0, 20])
    ax.set_title(f"t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
