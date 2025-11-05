# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_centrifugal_calc.py
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

rgrid = np.array([ r * dx - dx/2 for r in range(int(nr))])


output_folder = "./data/azim/eq_momentum_u/centrifugal/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")
    centrifugal = - data ** 2
    for r in range(nr):
        centrifugal[:,r] = centrifugal[:,r] / (rgrid[r])
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", centrifugal)

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
