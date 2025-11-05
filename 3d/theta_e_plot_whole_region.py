# python $WORK/tc_analyze/3d/theta_e_plot_whole_region.py $style
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


os.makedirs(str(f"./fig/3d/theta_e/whole_region/"),exist_ok=True)

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"./fig/3d/theta_e/whole_region/z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

def process_t(t):
    data_t = np.load(f"./data/3d/theta_e/t{str(t).zfill(3)}.npy")
    for z in z_list:
        data = data_t[z,:,:]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3,2.5))
        c = ax.contourf(X,Y,data, levels=np.arange(330,375,5), cmap="rainbow", extend="both")
        cbar = fig.colorbar(c, ax=ax)
        cbar.set_ticks([330,370])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"t={t}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(f"./fig/3d/theta_e/whole_region/z{str(z).zfill(2)}/t{str(time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(0,nt))
