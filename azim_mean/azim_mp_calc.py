# python $WORK/tc_analyze/azim_mean/azim_mp_calc.py
# 微物理のみ(phy - tb)
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

folder1 = f"./data/azim/mp_radial/"
folder2 = f"./data/azim/mp_tangential/"

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

# データの読み込み
data_all_phy_u = np.memmap(f"{input_folder}ms_phy_du.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))
data_all_phy_v = np.memmap(f"{input_folder}ms_phy_dv.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))
data_all_tb_u = np.memmap(f"{input_folder}ms_tb_du.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))
data_all_tb_v = np.memmap(f"{input_folder}ms_tb_dv.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))

# メインループ
def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5*x_width] -= x_width
    dX[dX < -0.5*x_width] += x_width

    theta = np.arctan2(dY, dX)

    R = np.sqrt(dX ** 2 + dY ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // dx).astype(int)
    count_r = np.bincount(bin_idx)

    data_u = data_all_phy_u[t] - data_all_tb_u[t]
    data_v = data_all_phy_v[t] - data_all_tb_v[t]

    valid_data_u = data_u[:, mask]
    valid_data_v = data_v[:, mask]

    v_radial = valid_data_u * np.cos(theta[mask]) + valid_data_v * np.sin(theta[mask])
    v_tangential = -valid_data_u * np.sin(theta[mask]) + valid_data_v * np.cos(theta[mask])

    azim_sum_radial = np.zeros((nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum_radial[:, b] += v_radial[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean_radial = np.where(count_r > 0, azim_sum_radial / count_r, np.nan)

    print(f"azim mean data t: {t}, max: {azim_mean_radial.max()}, min: {azim_mean_radial.min()}")
    np.save(f"{folder1}t{str(t).zfill(3)}.npy", azim_mean_radial)

    azim_sum_tangential = np.zeros((nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum_tangential[:, b] += v_tangential[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean_tangential = np.where(count_r > 0, azim_sum_tangential / count_r, np.nan)

    print(f"azim mean data t: {t}, max: {azim_mean_tangential.max()}, min: {azim_mean_tangential.min()}")
    np.save(f"{folder2}t{str(t).zfill(3)}.npy", azim_mean_tangential)

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
