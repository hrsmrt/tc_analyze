# python $WORK/tc_analyze/azim_q8/azim_q8_3d_calc.py varname
import os
import sys

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

varname = sys.argv[1]

r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(config.nx) + 0.5) * config.dx
y = (np.arange(config.ny) + 0.5) * config.dy
X, Y = np.meshgrid(x, y)

folder = f"./data/azim_q8/{varname}/"

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
    dX = X - cx
    dY = Y - cy
    # 周期境界条件を考慮
    dX = np.where(dX > config.x_width / 2, dX - config.x_width, dX)
    dX = np.where(dX < -config.x_width / 2, dX + config.x_width, dX)
    R = np.sqrt(dX**2 + dY**2)
    mask = R <= r_max
    valid_r = R[mask]

    theta = np.arctan2(dY[mask], dX[mask])
    theta[theta < 0] += 2 * np.pi
    theta = (theta - np.pi / 2) % (2 * np.pi)  # 北を0°にシフト
    sector = (theta // (np.pi / 4)).astype(int)  # 0〜7

    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    # 出力配列 (nz, max_bin, 8 sectors)
    azim_sum = np.zeros((config.nz, max_bin, 8))
    count_r = np.zeros((max_bin, 8), dtype=int)

    data = data_all[t]  # shape = (nz, ny, nx)
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    # valid_data は (nz, npoints)
    valid_data = data[:, mask]

    # bin × sector に振り分けて加算
    for i, (b, s) in enumerate(zip(bin_idx, sector)):
        azim_sum[:, b, s] += valid_data[:, i]
        count_r[b, s] += 1

    # 割り算（ゼロ割回避）
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r[np.newaxis, :, :], np.nan)

    print(
        f"azim mean data t: {t}, max: {np.nanmax(azim_mean)}, min: {np.nanmin(azim_mean)}"
    )

    np.save(f"{folder}t{str(t).zfill(3)}.npy", azim_mean)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
