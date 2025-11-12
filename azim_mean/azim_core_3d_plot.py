# python $WORK/tc_analyze/azim_mean/azim_core_3d_plot.py varname $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

varname = sys.argv[1]

if len(sys.argv) > 2:
    mpl_style_sheet = sys.argv[2]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

time_list = config.time_list

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

r_max = 1000e3
nr = int(np.floor(r_max / config.dx))
xgrid = np.arange(nr) * config.dx

X, Y = np.meshgrid(xgrid,vgrid)

folder = f"./fig/azim_core/{varname}/"

os.makedirs(folder,exist_ok=True)

def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim/{varname}/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    title_name = varname
    match varname:
        case "ms_u":
            c = ax.contourf(X, Y, data, levels=np.arange(-40,45,5), cmap="bwr", extend="both")
            cb = fig.colorbar(c, ax=ax)
            cb.set_ticks([-40,0,45])
        case "ms_v":
            c = ax.contourf(X, Y, data, levels=np.arange(-40,45,5), cmap="bwr", extend="both")
            cb = fig.colorbar(c, ax=ax)
            cb.set_ticks([-40,0,45])
        case "ms_w":
            c = ax.contourf(X, Y, data, levels=np.arange(-1,1.1,0.1), cmap="bwr", extend="both")
            cb = fig.colorbar(c, ax=ax)
            cb.set_ticks([-1,0,1])
            title_name = "鉛直風"
        case "ms_rh":
            c = ax.contourf(X, Y, data, levels=np.arange(0,1.2,0.1), cmap="rainbow", extend="max")
            cb = fig.colorbar(c, ax=ax)
            cb.set_ticks([0,1.0])
        case "ms_dh":
            c = ax.contourf(X, Y, data, levels=np.arange(0,0.001,0.0001), cmap="rainbow", extend="max")
            cb = fig.colorbar(c, ax=ax)
            cb.set_ticks([0,0.001])
        case _:
            c = ax.contourf(X, Y, data, cmap="rainbow", extend="both")
            fig.colorbar(c, ax=ax)
    ax.set_ylim([0, 20e3])
    ax.set_xlim([0,150e3])
    ax.set_xticks([0,50e3,100e3,150e3],[0,"","",150])
    ax.set_yticks([0,5e3,10e3,15e3,20e3],[0,"","","",20])
    ax.set_aspect("equal", "box")
    ax.set_title(f"方位角平均 {title_name} t = {time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")

    fig.savefig(f"{folder}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
