# python $WORK/tc_analyze/symmetrisity/3d_calc.py varname
import os
import sys
import numpy as np
from joblib import Parallel, delayed

varname = sys.argv[1]

# ファイルを開いてJSONを読み込む
from utils.config import AnalysisConfig

config = AnalysisConfig()

center_x_list = config.center_x
center_y_list = config.center_y

# データの読み込み
data_all = np.memmap(f"{config.input_folder}{varname}.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.nz, config.ny, config.nx))

# メインループ
def process_t(t):
    # 軸対称成分
    # 
    data_azim_mean = np.load(f"./data/azim/{varname}/t{str(t).zfill(3)}.npy")

    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]
    bin_idx = (valid_r // config.dx).astype(int)
    count_r = np.bincount(bin_idx)

    azim_mean = np.full((config.nz, len(count_r)), np.nan)

    data = data_all[t]
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[:, mask]
    azim_sum = np.zeros((config.nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum[:, b] += (valid_data[:, i] - data_azim_mean[:, b]) ** 2
    # 割り算（ゼロ割回避）
    with np.errstate(divide='ignore', invalid='ignore'):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)
    symmetrisity = data_azim_mean ** 2 / (data_azim_mean ** 2 + azim_mean + 1e-20)

    print(f"azim mean data t: {t}, max: {symmetrisity.max()}, min: {symmetrisity.min()}")
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", symmetrisity)

Parallel(n_jobs=n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
