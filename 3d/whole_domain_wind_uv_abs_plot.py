# python $WORK/tc_analyze/3d/whole_domain_wind_uv_abs_plot.py $style
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
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)

output_folder = f"./fig/3d/whole_domain/wind_uv_abs/"
os.makedirs(output_folder,exist_ok=True)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"{output_folder}z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

u_all = np.memmap(f"{input_folder}ms_u.grd", dtype=">f4", mode="r", shape=(nt,nz,ny,nx))
v_all = np.memmap(f"{input_folder}ms_v.grd", dtype=">f4", mode="r", shape=(nt,nz,ny,nx))

def process_t(t):
    for z in z_list:
        u = u_all[t,z,:,:]
        v = v_all[t,z,:,:]
        data = np.sqrt(u**2 + v**2)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(2.5,2))
        c = ax.contourf(X,Y,data,cmap="rainbow",levels=np.arange(5,70,5),extend='max')
        fig.colorbar(c, ax=ax)
        ax.set_title(f"t={time_list[t]}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_xticks([0, x_width * 1/2, x_width],["","",""])
        ax.set_yticks([0, y_width * 1/2, y_width],["","",""])
        ax.set_aspect("equal", "box")
        fig.savefig(f"{output_folder}z{str(z).zfill(2)}/t{str(time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=2)(delayed(process_t)(t) for t in range(0,nt,int(24/dt_hour)))
