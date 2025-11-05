# python $WORK/tc_analyze/3d/vorticity_z_absolute_whole_domain_plot.py $style
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
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
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']
f = setting['f']

time_list = [t * dt_hour for t in range(nt)]

output_dir = f"./fig/3d/whole_domain/vorticity_z_absolute/"
os.makedirs(output_dir,exist_ok=True)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"{output_dir}z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

x_axis = np.arange(0.5*dx,nx*dx,dx) * 1e-3
y_axis = np.arange(0.5*dy,ny*dy,dy) * 1e-3
X,Y = np.meshgrid(x_axis,y_axis)

def process_t(t):
  data_z = np.memmap(f"./data/3d/vorticity_z/vor_t{str(t).zfill(3)}.npy", dtype=np.float32, mode="r", shape=(nz, ny, nx))
  for z in z_list:
    data = data_z[z]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,4))
    c = ax.contourf(X,Y,data + f,cmap="rainbow")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(
        "right", size="5%", pad=0.1
    )  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    ax.set_title(f"t={time_list[t]:3d}h,z={int(vgrid[z]*1e-2)*1e-1}km")
    ax.grid(False)
    ax.set_aspect("equal", "box")
    fig.savefig(f"{output_dir}z{str(z).zfill(2)}/t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=1)(delayed(process_t)(t) for t in range(0,nt,int(24/dt_hour)))
