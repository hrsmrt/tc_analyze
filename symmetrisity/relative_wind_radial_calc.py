# python $WORK/tc_analyze/symmetrisity/relative_wind_radial_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

output_folder = "./data/symmetrisity/relative_wind_radial/"

os.makedirs(output_folder, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y


# メインループ
def process_t(t):
    # 軸対称成分
    data_azim_mean = np.load(f"./data/azim/wind_relative_radial/t{str(t).zfill(3)}.npy")
    max_bin = data_azim_mean.shape[1]  # azim_meanのビン数に合わせる

    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    # 周期境界条件を考慮した距離計算
    R = grid.calculate_radial_distance(cx, cy)
    mask = R <= r_max
    valid_r = R[mask]

    # 統一されたビニング方法
    bin_idx = np.floor(valid_r / config.dx).astype(int)
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    data = np.load(f"./data/3d/relative_wind_radial/t{str(t).zfill(3)}.npy")
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    valid_data = data[:, mask]
    azim_sum = np.zeros((config.nz, max_bin))
    count_r = np.zeros(max_bin, dtype=int)

    for i, b in enumerate(bin_idx):
        azim_sum[:, b] += (valid_data[:, i] - data_azim_mean[:, b]) ** 2
        count_r[b] += 1

    # 割り算（ゼロ割回避）
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)
    symmetrisity = data_azim_mean**2 / (data_azim_mean**2 + azim_mean + 1e-20)

    print(
        f"symmetrisity t: {t}, max: {np.nanmax(symmetrisity)}, min: {np.nanmin(symmetrisity)}"
    )
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", symmetrisity)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
