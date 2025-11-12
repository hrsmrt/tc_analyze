# python $WORK/tc_analyze/azim_mean/azim_pert_3d_plot.py varname $style
# 方位角平均データをプロット
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

varname = sys.argv[1]

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument
mpl_style_sheet = parse_style_argument()
config = AnalysisConfig()

time_list = config.time_list

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

r_max = 1000e3
nr = int(np.floor(r_max / config.dx))
xgrid = np.arange(nr) * config.dx * 1e-3

X, Y = np.meshgrid(xgrid,vgrid*1e-3)

folder = f"./fig/azim_pert/{varname}/"

os.makedirs(folder,exist_ok=True)

def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim_pert/{varname}/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    title_name = varname
    match varname:
        case "ms_tem":
            c = ax.contourf(X, Y, data, levels=np.arange(-10,12,2), cmap="bwr", extend="both")
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-10,0,10])
            title_name = "気温偏差"
        case "ms_pres":
            c = ax.contourf(X, Y, data*1e-2, levels=np.arange(-100,1,10), cmap="rainbow_r", extend="both")
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-100,0])
            title_name = "気圧偏差"
        case "ms_rho":
            c = ax.contourf(X, Y, data, levels=np.arange(-0.1,0.11,0.01), cmap="bwr_r", extend="both")
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-0.1,0,0.1])
            title_name = "密度偏差"
        case _:
            c = ax.contourf(X, Y, data, cmap="rainbow", extend="both")
            fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20])
    ax.set_xticks([0,250,500,750,1000],[0,"","","",1000])
    ax.set_yticks([0,5,10,15,20],[0,"","","",20])
    ax.set_title(f"方位角平均 {title_name} t = {time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")

    fig.savefig(f"{folder}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
