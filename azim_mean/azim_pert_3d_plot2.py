# python $WORK/tc_analyze/azim_mean/azim_pert_3d_plot2.py varname $style
# 方位角平均データをプロット
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
xgrid = np.arange(nr) * config.dx * 1e-3

X, Y = np.meshgrid(xgrid,vgrid*1e-3)

folder = f"./fig/azim_pert2/{varname}/"

os.makedirs(folder,exist_ok=True)

def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim_pert2/{varname}/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    title_name = varname
    match varname:
        case "ms_tem":
            c = ax.contourf(X[:60,:],Y[:60,:],data[:60,:], levels=20, cmap="seismic",vmax=4, vmin=-4)
            cbar = fig.colorbar(c, ax=ax)
            ax.set_xticks([0,1000])
            ax.set_ylim(0,20)
            ax.set_yticks([0,20])
            ax.minorticks_on()
            ax.grid(which='major', axis='both', color='gray', linewidth=0.8)
            ax.grid(which='minor', axis='both', color='gray', linestyle=':', linewidth=0.5)
            title_name = "気温偏差"
        case "ms_pres":
            c = ax.contourf(X,Y,data*1e-2, levels=20, cmap="jet_r")
            cbar = fig.colorbar(c, ax=ax)
            ax.set_xticks([0,1000])
            ax.minorticks_on()
            ax.grid(which='major', axis='both', color='gray', linewidth=0.8)
            ax.grid(which='minor', axis='both', color='gray', linestyle=':', linewidth=0.5)
            ax.set_ylim(0, 20)
            ax.set_yticks([0,20])
            title_name = "気圧偏差"
        case "ms_rho":
            c = ax.contourf(X,Y,data*1e2, levels=20, cmap="seismic", vmax=1.8, vmin=-1.8)
            cbar = fig.colorbar(c, ax=ax)
            ax.set_xticks([0,1000])
            ax.minorticks_on()
            ax.grid(which='major', axis='both', color='gray', linewidth=0.8)
            ax.grid(which='minor', axis='both', color='gray', linestyle=':', linewidth=0.5)
            ax.set_ylim(0, 20)
            ax.set_yticks([0,20])
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
