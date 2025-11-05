# python $WORK/tc_analyze/3d/vortex_region_r250.py varname $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
from joblib import Parallel, delayed

varname = sys.argv[1]


# コマンドライン引数が3つ以上あるかを確認
if len(sys.argv) > 2:
    mpl_style_sheet = sys.argv[2]
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
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

extent = 250e3
extent_x = int(np.ceil(extent / dx))
extent_y = int(np.ceil(extent / dy))

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

output_folder = f"./fig/3d/vortex_region_r250/{varname}/"
os.makedirs(output_folder,exist_ok=True)

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)
X_cut = X[: extent_y * 2, : extent_x * 2]
Y_cut = Y[: extent_y * 2, : extent_x * 2]

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"{output_folder}z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

data_all = np.memmap(f"{input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(nt,nz,ny,nx))


def process_t(t):
    center_x = int(center_x_list[t]/dx)
    center_y = int(center_y_list[t]/dy)
    x_idx = [(center_x - extent_x + i) % nx for i in range(2 * extent_x)]
    y_idx = [(center_y - extent_y + i) % ny for i in range(2 * extent_y)]
    for z in z_list:
        data = data_all[t,z,:,:]
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
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3,2.5))
        match varname:
            case "ms_u":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(-40,45,5),cmap="bwr",extend="both")
            case "ms_v":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(-40,45,5),cmap="bwr",extend="both")
            case "ms_w":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(-4,4.5,0.5),cmap="bwr",extend="both")
            case "ms_rh":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(0,1.2,0.1),cmap="rainbow",extend="both")
            case _:
                c = ax.contourf(X_cut,Y_cut,data_masked,cmap="rainbow")
        fig.colorbar(c, ax=ax)
        ax.set_xticks(
                [0, extent_x * dx, 2 * extent_x * dx],
                [-int(extent*1e-3), "0", int(extent*1e-3)],
            )
        ax.set_yticks(
            [0, extent_y * dy, 2 * extent_y * dy],
            [int(extent*1e-3), "0", -int(extent*1e-3)],
        )
        ax.set_title(f"t={t}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        #ax.set_xlabel("x [km]")
        #ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")
        fig.savefig(f"{output_folder}z{str(z).zfill(2)}/t{str(time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(0,nt,int(24/dt_hour)))
