"""
3次元変数の方位角平均計算（汎用版）

このスクリプトは、コマンドライン引数で指定された3次元変数の
方位角平均を計算します。

使用方法:
    python $WORK/tc_analyze/azim_mean/azim_3d_calc2.py varname

引数:
    varname: 計算対象の変数名
"""
# python $WORK/tc_analyze/azim_mean/azim_3d_calc2.py varname
import os
import sys

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

varname = sys.argv[1]

print(f"Calculating azimuthal mean for variable: {varname}")

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

X, Y = grid.X, grid.Y

output_folder = f"./data/azim2/{varname}/"

os.makedirs(output_folder, exist_ok=True)

center_list = np.loadtxt("./data/low_2.txt", delimiter=",", skiprows=1)
center_x_list = center_list[:, 1] * config.dx
center_y_list = center_list[:, 2] * config.dy

# データの読み込み
data_all = np.memmap(
    f"{config.input_folder}{varname}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


# メインループ
def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]

    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)  # 範囲外を防ぐ

    count_r = np.bincount(bin_idx, minlength=max_bin)

    azim_mean = np.full((config.nz, len(count_r)), np.nan)

    data = data_all[t]
    # print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[:, mask]
    azim_sum = np.zeros((config.nz, len(count_r)))
    for i, b in enumerate(bin_idx):
        azim_sum[:, b] += valid_data[:, i]
    # 割り算（ゼロ割回避）
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)

    # print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", azim_mean)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
