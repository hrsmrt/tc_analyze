# python $WORK/tc_analyze/azim_mean/azim_vorticity_z_calc.py
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

folder = f"./data/azim/vorticity_z/"

os.makedirs(folder,exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# メインループ
def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // config.dx).astype(int)
    count_r = np.bincount(bin_idx)

    azim_mean = np.full((config.nz, len(count_r)), np.nan)

    data = np.load(f"./data/3d/vorticity_z/vor_t{str(t).zfill(3)}.npy")
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[:, mask]
    azim_sum = np.zeros((config.nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum[:, b] += valid_data[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)

    print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.save(f"{folder}t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
