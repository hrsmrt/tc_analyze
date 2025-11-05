# python $WORK/tc_analyze/analyze/2d/ss_wind10m_abs_whole_domain.py $style
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
colors[:20] = [1, 1, 1, 1]  # 下限の20色を白に設定
custom_cmap = ListedColormap(colors)

output_dir = "./fig/2d/whole_domain/wind10m_abs/"
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

input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)

ss_u10m = np.fromfile(f"{input_folder}ss_u10m.grd",dtype=">f4").reshape(nt,ny,nx)
ss_v10m = np.fromfile(f"{input_folder}ss_v10m.grd",dtype=">f4").reshape(nt,ny,nx)
data_abs = np.sqrt(ss_v10m**2 + ss_u10m**2)

def process_t(t):
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2,2))
    c = ax.contourf(X,Y,data_abs[t],cmap=custom_cmap,levels=np.arange(0,51,5),extend='max')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    ax.set_xticks([0, x_width * 1/2, x_width],["","",""])
    ax.set_yticks([0, y_width * 1/2, y_width],["","",""])
    ax.set_title(f"10m風速 t = {time_list[t]} h")
    ax.set_aspect('equal', 'box')
    ax.grid(False)
    fig.savefig(f"{output_dir}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
