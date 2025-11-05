# python $WORK/tc_analyze/azim_mean/eliassen/azim_N2_plot.py $style
# N^2のi+1/2上の値

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
from joblib import Parallel, delayed

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    plt.style.use(mpl_style_sheet)
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
triangle_size = setting['triangle_size']
nx = 2 ** glevel
x_width = triangle_size
dx = x_width / nx

vgrid = np.loadtxt(f"{os.path.dirname(os.path.abspath(__file__))}/../../database/vgrid/vgrid_c74.txt")

vgrid_wall = (vgrid[:-1] + vgrid[1:]) / 2  # i+1/2の位置

time_list = [t * dt_hour for t in range(nt)]

r_max = 1000e3

nr = int(r_max / dx)
R= (np.arange(nr)) * dx + dx/2
f = 3.77468e-5

X, Y = np.meshgrid(R, vgrid_wall)

input_folder = "./data/azim/eliassen/N2/"
output_folder = "./fig/azim/eliassen/N2/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(f"{input_folder}t{str(t).zfill(3)}.npy")
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    c = ax.contourf(X*1e-3, Y*1e-3, data, cmap="rainbow", extend="both")
    cbar = fig.colorbar(c,ax=ax)
    #cbar.set_ticks([300,400])
    ax.set_ylim([0,20])
    ax.set_title(f"$N^2$ t = {time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done(max:{data.max()},min:{data.min()})")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
