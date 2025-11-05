# python $WORK/p-nicam/analyze/3d/divergence_calc.py
import os
import sys
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
nz = setting['nz']
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']

folder = f"./data/3d/divergence/"

os.makedirs(folder, exist_ok=True)

data_all_u = np.memmap(f"{input_folder}/ms_u.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))
data_all_v = np.memmap(f"{input_folder}/ms_v.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))

def process_t(t):
    # (nz, ny, nx) の配列を取得
    data_u = data_all_u[t]  # shape: (nz, ny, nx)
    data_v = data_all_v[t]  # shape: (nz, ny, nx)

    div = np.zeros((nz, ny, nx), dtype=np.float32)
    for z in range(nz):
        du_dx = (np.roll(data_u[z], -1, axis=1) - np.roll(data_u[z], 1, axis=1)) / (2 * dx)
        dv_dy = (np.roll(data_v[z], -1, axis=0) - np.roll(data_v[z], 1, axis=0)) / (2 * dy)
        dv_dy[0, :nx//2] = (data_v[z, 1, :nx//2] - data_v[z, -1, nx//2:]) / (2 * dy)
        dv_dy[0, nx//2:] = (data_v[z, 1, nx//2:] - data_v[z, -1, :nx//2]) / (2 * dy)
        dv_dy[-1, :nx//2] = (data_v[z, 0, :nx//2] - data_v[z, -2, nx//2:]) / (2 * dy)
        dv_dy[-1, nx//2:] = (data_v[z, 0, nx//2:] - data_v[z, -2, :nx//2]) / (2 * dy)
        div[z] = du_dx + dv_dy
    np.save(f"{folder}div_t{str(t).zfill(3)}.npy", div)
    print(f"t: {t} divergence calc done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
