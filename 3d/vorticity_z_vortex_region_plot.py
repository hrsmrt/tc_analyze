# python $WORK/tc_analyze/3d/vorticity_z_vortex_region_plot.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
from joblib import Parallel, delayed

# コマンドライン引数が3つ以上あるかを確認
if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
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
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny

time_list = [t * dt_hour for t in range(nt)]

extent = 500e3
extent_x = int(extent / dx)
extent_y = int(extent / dy)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

os.makedirs(str(f"./fig/3d/vortex_region/vorticity_z/"),exist_ok=True)

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)
X_cut = X[: extent_y * 2, : extent_x * 2]
Y_cut = Y[: extent_y * 2, : extent_x * 2]

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"./fig/3d/vortex_region/vorticity_z/z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

def process_t(t):
    data_t = np.load(f"./data/3d/vorticity_z/vor_t{str(t).zfill(3)}.npy")
    center_x = int(center_x_list[t]/dx)
    center_y = int(center_y_list[t]/dy)
    x_idx = [(center_x - extent_x + i) % nx for i in range(2 * extent_x)]
    y_idx = [(center_y - extent_y + i) % ny for i in range(2 * extent_y)]
    for z in z_list:
        data = data_t[z,:,:]
        data_cut = data[np.ix_(y_idx, x_idx)]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3,2.5))
        c = ax.contourf(X_cut,Y_cut,data_cut,cmap="bwr", levels=np.arange(-0.002,0.0022,0.0002),extend='both')
        cbar = fig.colorbar(c, ax=ax)
        cbar.set_ticks([-0.002,0.002])
        ax.set_xticks(
                [0, extent_x * dx, 2 * extent_x * dx],
                ["", "", ""],
            )
        ax.set_yticks(
            [0, extent_y * dy, 2 * extent_y * dy],
            ["", "", ""],
        )
        ax.set_title(f"t={t}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(f"./fig/3d/vortex_region/vorticity_z/z{str(z).zfill(2)}/t{str(time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(0,nt,int(24/dt_hour)))
