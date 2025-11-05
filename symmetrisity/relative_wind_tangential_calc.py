# python $WORK/tc_analyze/symmetrisity/relative_wind_tangential_calc.py
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
from joblib import Parallel, delayed
import json


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

output_folder = f"./data/symmetrisity/relative_wind_tangential/"

os.makedirs(output_folder,exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

rgrid = np.array([ r * dx + dx/2 for r in range(int(r_max/dx))])

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

# メインループ
def process_t(t):
    # 軸対称成分
    data_azim_mean = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")

    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // dx).astype(int)
    count_r = np.bincount(bin_idx)

    azim_mean = np.full((nz, len(count_r)), np.nan)

    data = np.load(f"./data/3d/relative_wind_tangential/t{str(t).zfill(3)}.npy")
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[:, mask]
    azim_sum = np.zeros((nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum[:, b] += (valid_data[:, i] - data_azim_mean[:, b]) ** 2
    
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)
    symmetrisity = data_azim_mean ** 2 / (data_azim_mean ** 2 + azim_mean + 1e-20)

    print(f"azim mean data t: {t}, max: {symmetrisity.max()}, min: {symmetrisity.min()}")
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", symmetrisity)

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
