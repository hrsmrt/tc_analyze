# python $WORK/tc_analyze/azim_mean/azim_wind_calc.py
import os
import sys
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

X, Y = grid.X, grid.Y

folder1 = f"./data/azim/wind_radial/"
folder2 = f"./data/azim/wind_tangential/"

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# データの読み込み
data_all_u = np.memmap(f"{config.input_folder}ms_u.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.nz, config.ny, config.nx))
data_all_v = np.memmap(f"{config.input_folder}ms_v.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.nz, config.ny, config.nx))

# メインループ
def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5*config.x_width] -= config.x_width
    dX[dX < -0.5*config.x_width] += config.x_width

    theta = np.arctan2(dY, dX)

    R = np.sqrt(dX ** 2 + dY ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // config.dx).astype(int)
    count_r = np.bincount(bin_idx)

    data_u = data_all_u[t]
    data_v = data_all_v[t]

    valid_data_u = data_u[:, mask]
    valid_data_v = data_v[:, mask]

    v_radial = valid_data_u * np.cos(theta[mask]) + valid_data_v * np.sin(theta[mask])
    v_tangential = -valid_data_u * np.sin(theta[mask]) + valid_data_v * np.cos(theta[mask])

    azim_sum_radial = np.zeros((config.nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum_radial[:, b] += v_radial[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean_radial = np.where(count_r > 0, azim_sum_radial / count_r, np.nan)

    print(f"azim mean data t: {t}, max: {azim_mean_radial.max()}, min: {azim_mean_radial.min()}")
    np.save(f"{folder1}t{str(t).zfill(3)}.npy", azim_mean_radial)

    azim_sum_tangential = np.zeros((config.nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum_tangential[:, b] += v_tangential[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean_tangential = np.where(count_r > 0, azim_sum_tangential / count_r, np.nan)

    print(f"azim mean data t: {t}, max: {azim_mean_tangential.max()}, min: {azim_mean_tangential.min()}")
    np.save(f"{folder2}t{str(t).zfill(3)}.npy", azim_mean_tangential)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
