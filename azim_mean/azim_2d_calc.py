# python $WORK/tc_analyze/azim_mean/azim_2d_calc.py varname
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import json
from joblib import Parallel, delayed

varname = sys.argv[1]

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

r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(nx) + 0.5) * dx
y = (np.arange(ny) + 0.5) * dy
X, Y = np.meshgrid(x, y)

folder = f"./data/azim/{varname}/"

os.makedirs(folder,exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // dx).astype(int)
    count_r = np.bincount(bin_idx)

    azim_mean = np.full((len(count_r)), np.nan)

    # データの読み込み
    count_2d = nx * ny
    offset = count_2d * t * 4
    with open(f"{input_folder}{varname}.grd", "rb") as f:
        f.seek(offset)
        data = np.fromfile(f, dtype=">f4", count=count_2d)
    data = data.reshape(ny, nx)
    print(f"2d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[mask]
    data_r = np.bincount(bin_idx, weights=valid_data)

    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean = np.where(count_r > 0, data_r / count_r, np.nan)
    print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.save(f"{folder}t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
