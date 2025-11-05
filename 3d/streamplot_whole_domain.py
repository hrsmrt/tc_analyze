# python $WORK/tc_analyze/3d/streamplot_whole_domain.py $style
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import matplotlib.pyplot as plt
import json
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
nz = setting['nz']
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(nx) + 0.5) * dx
y = (np.arange(ny) + 0.5) * dy
X, Y = np.meshgrid(x, y)

z_list = [0,9,17,23,29,36,42,48,54,60]

folder = f"./fig/3d/whole_domain/streamplot/"
os.makedirs(folder, exist_ok=True)

for z in z_list:
  os.makedirs(f"./fig/3d/whole_domain/streamplot/z{str(z).zfill(2)}",exist_ok=True)

data_all_u = np.memmap(f"{input_folder}/ms_u.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))
data_all_v = np.memmap(f"{input_folder}/ms_v.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))

def process_t(t):
    data_u = data_all_u[t]  # shape: (nz, ny, nx)
    data_v = data_all_v[t]  # shape: (nz, ny, nx)
    for z in z_list:
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(4,3))
        ax.streamplot(X, Y, data_u[z], data_v[z])
        ax.set_title(f"t={t*dt_hour}h z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        fig.savefig(f"./fig/3d/whole_domain/streamplot/z{str(z).zfill(2)}/t{str(t).zfill(3)}.png")
        plt.close()
    print(f"t: {t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(0,nt,int(24/dt_hour)))
