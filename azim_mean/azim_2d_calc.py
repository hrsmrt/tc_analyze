# python $WORK/tc_analyze/azim_mean/azim_2d_calc.py varname
import os
import sys
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

varname = sys.argv[1]

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

X, Y = grid.X, grid.Y

folder = f"./data/azim/{varname}/"

os.makedirs(folder,exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // config.dx).astype(int)
    count_r = np.bincount(bin_idx)

    azim_mean = np.full((len(count_r)), np.nan)

    # データの読み込み
    count_2d = config.nx * config.ny
    offset = count_2d * t * 4
    with open(f"{config.input_folder}{varname}.grd", "rb") as f:
        f.seek(offset)
        data = np.fromfile(f, dtype=">f4", count=count_2d)
    data = data.reshape(config.ny, config.nx)
    print(f"2d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[mask]
    data_r = np.bincount(bin_idx, weights=valid_data)

    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean = np.where(count_r > 0, data_r / count_r, np.nan)
    print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.save(f"{folder}t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
