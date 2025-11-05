# nohup python $WORK/tc_analyze/3d/zeta_absolute_plot.py $style &
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "module"))
sys.path.append(module_path)
from input_data import read_fortran_unformatted
import json
from joblib import Parallel, delayed

if len(sys.argv) > 1:
  mpl_style_sheet = sys.argv[1]

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

f = setting['f']

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

extent = 500e3
extent_x = int(extent / dx)
extent_y = int(extent / dy)

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)
X_cut = X[: extent_y * 2, : extent_x * 2]
Y_cut = Y[: extent_y * 2, : extent_x * 2]

z_list = [0,10,13,27,30,36,42,48,54,60]

output_dir = "./fig/3d/zeta_absolute/"
os.makedirs(output_dir,exist_ok=True)
for z in z_list:
    os.makedirs(f"{output_dir}z{str(z+1).zfill(2)}",exist_ok=True)


center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

def process_t(t):
    center_x = int(center_x_list[t]/dx)
    center_y = int(center_y_list[t]/dy)
    x_idx = [(center_x - extent_x + i) % nx for i in range(2 * extent_x)]
    y_idx = [(center_y - extent_y + i) % ny for i in range(2 * extent_y)]
    for z in z_list:
        filename = f"t{str(t+1).zfill(4)}z{str(z+1).zfill(2)}.dat"
        filepath = f"./data/zeta/{filename}"
        data = read_fortran_unformatted(filepath, np.float32)
        data = data.reshape(ny,nx)
        data_cut = data[np.ix_(y_idx, x_idx)]
        # === 中心から半径 R 以内のみプロット ===
        R_plot_max = 500e3  # 500 km
        cx = X_cut.mean()  # グリッドの中心を近似
        cy = Y_cut.mean()
        # 半径距離
        R = np.sqrt((X_cut - cx)**2 + (Y_cut - cy)**2)

        # 半径 R 内だけプロットするマスク
        mask = R <= R_plot_max  
        data_masked = np.where(mask, data_cut, np.nan)  # 外側は NaN に
        data_masked += f
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(2.5,2))
        pc = ax.contourf(X_cut,Y_cut,data_masked,levels=np.linspace(-0.004,0.004,12),cmap="seismic",extend="both")
        cbar = fig.colorbar(pc, ax=ax)
        cbar.set_ticks([-0.004, 0, 0.004])
        ax.set_aspect('equal', adjustable='box')
        ax.set_xticks(
                [0, extent_x * dx, 2 * extent_x * dx],
                ["","",""],
            )
        ax.set_yticks(
                [0, extent_y * dy, 2 * extent_y * dy],
                ["","",""],
            )
        ax.set_title(f"t = {t:3d}h, z = {int(vgrid[z]*1e-2)*1e-1}km")

        plt.savefig(f"{output_dir}z{str(z+1).zfill(2)}/t{str(t).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(0,nt,int(dt_hour)))
