# python $WORK/tc_analyze/azim_mean/eq_momentum_w/azim_wdw_dz_calc.py
import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
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

time_list = [t * dt_hour for t in range(nt)]

radius = 1000e3

nr = int(radius / dx)

rgrid = np.array([ r * dx - dx/2 for r in range(int(nr))]) * 1e-3
vgrid = np.loadtxt(f"{script_dir}/../../../database/vgrid/vgrid_c74.txt")

output_folder = "./data/azim/eq_momentum_w/wdw_dz/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/ms_w/t{str(t).zfill(3)}.npy")
    wdu_dz = np.empty((nz-1, nr))
    for z in range(nz-1):
        wdu_dz[z,:] = (data[z+1,:] + data[z,:]) * 0.5 * (data[z+1,:] - data[z,:]) / (vgrid[z+1] - vgrid[z])
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", wdu_dz)

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
