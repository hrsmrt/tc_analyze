# python $WORK/tc_analyze/azim_q8/azim_q8_wind_relative_calc.py
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
n_jobs = setting.get("n_jobs", 1)



r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(nx) + 0.5) * dx
y = (np.arange(ny) + 0.5) * dy
X, Y = np.meshgrid(x, y)

output_folder1 = f"./data/azim_q8/wind_relative_radial/"
output_folder2 = f"./data/azim_q8/wind_relative_tangential/"

os.makedirs(output_folder1, exist_ok=True)
os.makedirs(output_folder2, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# メインループ
def process_t(t):
    cx = center_x_list[t]
    cy = center_y_list[t]
    dX = X - cx
    dY = Y - cy
    dX[dX >  0.5*x_width] -= x_width
    dX[dX < -0.5*x_width] += x_width
    R = np.sqrt(dX**2 + dY**2)
    mask = R <= r_max
    valid_r = R[mask]

    theta_raw = np.arctan2(dY[mask], dX[mask])   # 東=0基準
    theta_raw[theta_raw < 0] += 2*np.pi

    # セクター分けだけ北基準にシフト
    theta = (theta_raw - np.pi/2) % (2*np.pi)
    sector = (theta // (np.pi/4)).astype(int)

    bin_idx = (valid_r // dx).astype(int)
    nbins = bin_idx.max() + 1

    # 出力配列
    azim_sum_radial     = np.zeros((nz, nbins, 8), dtype=np.float64)
    count_r_radial      = np.zeros((nbins, 8), dtype=np.int64)
    azim_sum_tangential = np.zeros((nz, nbins, 8), dtype=np.float64)
    count_r_tangential  = np.zeros((nbins, 8), dtype=np.int64)

    # データを読み込む
    data_u = np.load(f"./data/3d/relative_u/t{str(t).zfill(3)}.npy", mmap_mode="r")
    data_v = np.load(f"./data/3d/relative_v/t{str(t).zfill(3)}.npy", mmap_mode="r")

    # === メモリ削減: 1点ごとに加算 ===
    idxs = np.where(mask.ravel())[0]  # 2D→1D index
    for k, (b, s) in enumerate(zip(bin_idx, sector)):
        iy, ix = np.unravel_index(idxs[k], X.shape)

        ucol = data_u[:, iy, ix]  # shape (nz,)
        vcol = data_v[:, iy, ix]

        # 局所極座標変換
        # 速度分解は raw θ を使う
        th = theta_raw[k]
        vr =  ucol*np.cos(th) + vcol*np.sin(th)
        vt = -ucol*np.sin(th) + vcol*np.cos(th)

        azim_sum_radial[:, b, s]     += vr
        count_r_radial[b, s]         += 1
        azim_sum_tangential[:, b, s] += vt
        count_r_tangential[b, s]     += 1

    # 割り算
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean_radial = np.where(count_r_radial[np.newaxis,:,:] > 0,
                                    azim_sum_radial / count_r_radial[np.newaxis,:,:],
                                    np.nan)
        azim_mean_tangential = np.where(count_r_tangential[np.newaxis,:,:] > 0,
                                        azim_sum_tangential / count_r_tangential[np.newaxis,:,:],
                                        np.nan)

    np.save(f"{output_folder1}t{str(t).zfill(3)}.npy", azim_mean_radial.astype(np.float32))
    np.save(f"{output_folder2}t{str(t).zfill(3)}.npy", azim_mean_tangential.astype(np.float32))

    print(f"t={t}: radial [{np.nanmin(azim_mean_radial)}, {np.nanmax(azim_mean_radial)}], "
          f"tangential [{np.nanmin(azim_mean_tangential)}, {np.nanmax(azim_mean_tangential)}]")

Parallel(n_jobs=n_jobs)(delayed(process_t)(t) for t in range(nt))
