# python $WORK/tc_analyze/z_profile/zeta_plot.py $style

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, '../../module')
sys.path.append(target_path)
import numpy as np
import matplotlib.pyplot as plt
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
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

vgrid = np.loadtxt(script_dir + "/../../database/vgrid/vgrid_c74.txt")

X, Y = np.meshgrid(time_list, vgrid*1e-3)

out_dir = f"./fig/z_profile/zeta/"
os.makedirs(out_dir,exist_ok=True)

data_all = np.load(f"./data/z_profile/zeta/z_zeta.npy")

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(7,2.5))
ax.set_xlim(0,time_list[-1])
ax.set_ylim(0,20)
ax.set_xticks([0,24,48,72,96,120,144,168,192,216,240])
ax.set_title(f"渦度")
ax.set_ylabel('高度 [km]')
ax.set_xlabel('時間 [hour]')
c = ax.contourf(X,Y,data_all.T,levels=np.arange(0,0.00022,0.00002),cmap="rainbow",extend="max")
fig.colorbar(c, ax=ax)
fig.savefig(os.path.join(out_dir, f'all.png'))
plt.close()

def process_t(t):
    data = data_all[t, :]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(data,vgrid*1e-3)
    ax.set_xlim(-0.00005,0.00025)
    ax.set_ylim(0,20)
    ax.set_ylabel('高度 [km]')
    ax.set_xlabel('')
    ax.set_title(f't = {time_list[t]} hour')
    fig.savefig(os.path.join(out_dir, f't{time_list[t]:04d}h.png'))
    plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
