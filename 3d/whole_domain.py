# python $WORK/tc_analyze/3d/whole_domain.py varname $style
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

os.makedirs(str(f"./fig/3d/whole_domain/{varname}"),exist_ok=True)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"./fig/3d/whole_domain/{varname}/z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

x_axis = np.arange(0.5*dx,nx*dx,dx)
y_axis = np.arange(0.5*dy,ny*dy,dy)
X,Y = np.meshgrid(x_axis,y_axis)

data_memmap = np.memmap(f"{input_folder}{varname}.grd",dtype=">f4",mode="r",shape=(nt,nz,ny,nx))

def process_t(t):
  for z in z_list:
    data = data_memmap[t,z,:,:]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,4))
    match varname:
        case "ms_u":
          c = ax.contourf(X,Y,data,levels=np.arange(-40,45,5),cmap="bwr",extend="both")
        case "ms_v":
          c = ax.contourf(X,Y,data,levels=np.arange(-40,45,5),cmap="bwr",extend="both")
        case "ms_w":
          c = ax.contourf(X,Y,data,levels=np.arange(-4,4.5,0.5),cmap="bwr",extend="both")
        case "ms_tem":
          if z == 0:
             c = ax.contourf(X,Y,data,levels=np.arange(295,305,1),cmap="rainbow",extend="both")
          else:
             c = ax.contourf(X,Y,data,cmap="rainbow",extend="both")
        case "ms_rh":
            c = ax.contourf(X,Y,data,levels=np.arange(0,1.2,0.1),cmap="rainbow",extend="both")
        case "ms_qv":
            if z == 0:
                c = ax.contourf(X,Y,data,levels=np.arange(0.005,0.027,0.002),cmap="rainbow",extend="both")
            else:
                c = ax.contourf(X,Y,data,cmap="rainbow",extend="both")
        case _:
          c = ax.contourf(X,Y,data,cmap="rainbow")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(
        "right", size="5%", pad=0.1
    )  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    ax.set_title(f"t={time_list[t]:3d}h,z={int(vgrid[z]*1e-2)*1e-1}km")
    ax.set_xticks(
        [0, x_width / 2, x_width],
        ["","",""],
    )
    ax.set_yticks(
        [0, y_width / 2, y_width],
        ["","",""],
    )
    # ax.set_xlabel("x [km]")
    # ax.set_ylabel("y [km]")
    ax.grid(False)
    ax.set_aspect("equal", "box")
    fig.savefig(f"./fig/3d/whole_domain/{varname}/z{str(z).zfill(2)}/t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=1)(delayed(process_t)(t) for t in range(0,nt,int(24/dt_hour)))
