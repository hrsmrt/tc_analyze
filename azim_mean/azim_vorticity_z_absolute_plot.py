# python $WORK/tc_analyze/azim_mean/azim_vorticity_z_absolute_plot.py $style

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

f = setting["f"]

vgrid = np.loadtxt(f"{os.path.dirname(os.path.abspath(__file__))}/../../database/vgrid/vgrid_c74.txt")

time_list = [t * dt_hour for t in range(nt)]

r_max = 1000e3

nr = int(r_max / dx)
R = (np.arange(nr) + 0.5) * dx

X, Y = np.meshgrid(R, vgrid)

input_folder = "./data/azim/vorticity_z/"
output_folder = "./fig/azim/vorticity_z_absolute/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    data = np.load(f"{input_folder}t{str(t).zfill(3)}.npy")
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,2))
    c = ax.contourf(X*1e-3, Y*1e-3, data + f,levels=np.arange(-0.001,0.0011,0.0001), cmap="bwr", extend="both")
    cbar = fig.colorbar(c,ax=ax)
    ax.set_xticks([0,250,500,750,1000],[0,"","","",1000])
    ax.set_ylim([0,20])
    ax.set_title(f"渦度 t = {time_list[t]} hour")
    fig.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
