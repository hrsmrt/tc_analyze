# python $WORK/tc_analyze/3d/relative_wind_radial_tangential_calc.py
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

r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(nx) + 0.5) * dx
y = (np.arange(ny) + 0.5) * dy
X, Y = np.meshgrid(x, y)

folder1 = f"./data/3d/relative_wind_radial/"
folder2 = f"./data/3d/relative_wind_tangential/"

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5 * x_width] -= x_width
    dX[dX < -0.5 * x_width] += x_width
    theta = np.arctan2(dY, dX)

    # (nz, ny, nx) の配列を取得
    data_u = np.load(f"./data/3d/relative_u/t{str(t).zfill(3)}.npy")  # shape: (nz, ny, nx)
    data_v = np.load(f"./data/3d/relative_v/t{str(t).zfill(3)}.npy")  # shape: (nz, ny, nx)

    # ブロードキャストで一括計算
    v_radial = data_u * np.cos(theta) + data_v * np.sin(theta)
    v_tangential = -data_u * np.sin(theta) + data_v * np.cos(theta)

    np.save(f"{folder1}/t{str(t).zfill(3)}.npy", v_radial)
    np.save(f"{folder2}/t{str(t).zfill(3)}.npy", v_tangential)

    print(f"t: {t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
