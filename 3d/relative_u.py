# python $WORK/tc_analyze/3d/relative_u.py
import os
import numpy as np
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
import json
from joblib import Parallel, delayed

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

os.makedirs(str(f"./data/3d/relative_u"),exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

x_axis = np.arange(0.5*dx,nx*dx,dx) * 1e-3
y_axis = np.arange(0.5*dy,ny*dy,dy) * 1e-3
X,Y = np.meshgrid(x_axis,y_axis)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")

center_u_list = np.zeros(nt)
center_u_list[1:-1] = (center_x_list[2:] - center_x_list[:-2]) / (2 * dt)
center_u_list[0] = (center_x_list[1] - center_x_list[0]) / (dt)
center_u_list[-1] = (center_x_list[-1] - center_x_list[-2]) / (dt)

data_memmap = np.memmap(f"{input_folder}ms_u.grd",dtype=">f4",mode="r",shape=(nt,nz,ny,nx))

def process_t(t):
    data = data_memmap[t,:,:,:]
    data_rel = data - center_u_list[t]
    np.save(f"./data/3d/relative_u/t{str(t).zfill(3)}.npy",data_rel)
    print(f"Saved: ./data/3d/relative_u/t{str(t).zfill(3)}.npy")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(0,nt))
