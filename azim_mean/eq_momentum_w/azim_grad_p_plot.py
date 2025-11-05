# python $WORK/tc_analyze/azim_mean/eq_momentum_w/azim_grad_p_plot.py $style
import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import matplotlib.pyplot as plt
import json
from joblib import Parallel, delayed

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

radius = 1000e3

nr = int(radius / dx)

vgrid = np.loadtxt(f"{script_dir}/../../../database/vgrid/vgrid_c74.txt")
vgrid = vgrid*1e-3
vgrid_wall = np.array([ (vgrid[z] + vgrid[z+1]) * 0.5 for z in range(nz-1)])
rgrid = np.array([ r * dx + dx/2 for r in range(int(nr))]) * 1e-3

X,Y = np.meshgrid(rgrid,vgrid_wall)

output_folder = "./fig/azim/eq_momentum_w/grad_p/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
  data = np.load(f"./data/azim/eq_momentum_w/grad_p/t{str(t).zfill(3)}.npy")

  plt.style.use(mpl_style_sheet)
  fig, ax = plt.subplots(figsize=(5,2))
  c = ax.contourf(X,Y,data,cmap="bwr",levels=np.arange(-0.01,0.011,0.001),extend="both")
  cbar = fig.colorbar(c, ax=ax)
  cbar.set_ticks([-0.01,0,0.01])
  ax.set_title(f"鉛直気圧傾度 t = {time_list[t]} hour")
  ax.set_ylim([0, 20])
  ax.set_xlabel("半径 [km]")
  ax.set_ylabel("高度 [km]")
  #plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
  plt.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
  plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
