# python $WORK/tc_analyze/analyze/2d/ss_wind10m_radial_plot.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "module"))
sys.path.append(module_path)
import json
from joblib import Parallel, delayed

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:40] = [1, 1, 1, 1]  # 0に相当する位置（真ん中）を白に変更
custom_cmap = ListedColormap(colors)

folder_input = "./data/2d/wind10m_radial/"
output_dir = "./fig/2d/vortex_region/wind10m_radial/"
os.makedirs(output_dir,exist_ok=True)

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

extent = 500e3
extent_x = int(extent / dx)
extent_y = int(extent / dy)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)
X_cut = X[: extent_y * 2, : extent_x * 2]
Y_cut = Y[: extent_y * 2, : extent_x * 2]

def process_t(t):
    center_x = int(center_x_list[t] / dx)
    center_y = int(center_y_list[t] / dy)
    data = np.load(f"{folder_input}t{str(t).zfill(3)}.npy")
    x_idx = [(center_x - extent_x + i) % nx for i in range(2*extent_x)]
    y_idx = [(center_y - extent_y + i) % ny for i in range(2*extent_y)]
    data_cut = data[np.ix_(y_idx, x_idx)]

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5,2.5))
    c = ax.contourf(X_cut*1e-3,Y_cut*1e-3,data_cut,cmap=custom_cmap,levels=np.arange(0,5.5,0.5),extend='max')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    ax.set_xticks([0, extent_x * dx * 1e-3, 2 * extent_x * dx * 1e-3],[])
    ax.set_yticks([0, extent_y * dy * 1e-3, 2 * extent_y * dy * 1e-3],[])
    # ax.set_xticks([0, extent_x * dx * 1e-3, 2 * extent_x * dx * 1e-3],[-int(extent_x * dx * 1e-3),0, int(extent_x * dx * 1e-3)])
    # ax.set_yticks([0, extent_y * dy * 1e-3, 2 * extent_y * dy * 1e-3],[-int(extent_y * dy * 1e-3),0, int(extent_y * dy * 1e-3)])
    # ax.set_xlabel("x [km]")
    # ax.set_ylabel("y [km]")

    ax.set_aspect('equal', 'box')
    plt.savefig(f"{output_dir}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
