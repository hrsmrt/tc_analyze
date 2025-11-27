# python $WORK/tc_analyze/azim_mean/azim_pert_3d_calc.py varname
# grdデータから方位角平均を計算し、環境場(渦中心からr_max以遠)との差をとる
from utils.grid import GridHandler
from utils.config import AnalysisConfig
import os
import sys

import numpy as np
from joblib import Parallel, delayed

varname = sys.argv[1]


config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

X, Y = grid.X, grid.Y

folder = config.get_data_path("azim_pert", varname)

os.makedirs(folder, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

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
    mask_outside = ~mask
    valid_r = R[mask]

    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)  # 範囲外を防ぐ

    count_r = np.bincount(bin_idx, minlength=max_bin)

    azim_mean = np.full((config.nz, len(count_r)), np.nan)

    data = data_all[t]
    # print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    masked_data = np.where(mask_outside, data, np.nan)  # mask_outsideがFalseの場所はNaN
    mean_outside = np.nanmean(masked_data, axis=(1, 2))

    valid_data = data[:, mask]

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for i, b in enumerate(bin_idx): azim_sum[:, b] += valid_data[:, i]
    azim_sum = np.zeros((config.nz, len(count_r)), dtype=np.float32)
    np.add.at(azim_sum.T, bin_idx, valid_data.T)

    # 割り算（ゼロ割回避）
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)
    azim_mean -= mean_outside[:, np.newaxis]
    # print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.save(os.path.join(folder, f"t{str(t).zfill(3)}.npy"), azim_mean)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
