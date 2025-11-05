# python $WORK/tc_analyze/azim_mean/azim_pert_3d_calc.py varname
# grdデータから方位角平均を計算し、環境場(渦中心からr_max以遠)との差をとる
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
from joblib import Parallel, delayed
import json

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

folder = f"./data/azim_pert/{varname}/"

os.makedirs(folder,exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

# データの読み込み
data_all = np.memmap(f"{input_folder}{varname}.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))

# メインループ
def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    mask_outside = ~mask
    valid_r = R[mask]

    bin_idx = np.floor(valid_r / dx).astype(int)
    max_bin = int(np.floor(r_max / dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)  # 範囲外を防ぐ

    count_r = np.bincount(bin_idx, minlength=max_bin)

    azim_mean = np.full((nz, len(count_r)), np.nan)

    data = data_all[t]
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")
    
    masked_data = np.where(mask_outside, data, np.nan)  # mask_outsideがFalseの場所はNaN
    mean_outside = np.nanmean(masked_data, axis=(1,2))

    valid_data = data[:, mask]
    azim_sum = np.zeros((nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum[:, b] += valid_data[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)
    azim_mean -= mean_outside[:, np.newaxis]
    print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.save(f"{folder}t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
