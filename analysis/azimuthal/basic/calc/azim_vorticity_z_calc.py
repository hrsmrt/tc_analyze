"""
z方向渦度の方位角平均を計算

✅ ストレージ節約版: オンデマンド計算を使用
事前計算されたvorticity_zデータの保存が不要

input: ms_u.grd, ms_v.grd, center位置
output: z方向渦度の方位角平均

python $WORK/tc_analyze/azim_mean/azim_vorticity_z_calc.py
"""

import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.vorticity import calculate_vorticity_z

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

X, Y = grid.X, grid.Y

folder = config.get_tc_centric_path("azimuthal", "basic/vorticity_z")

os.makedirs(folder, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く
data_all_u = np.memmap(
    f"{config.input_folder}ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_all_v = np.memmap(
    f"{config.input_folder}ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    mask = R <= r_max
    valid_r = R[mask]

    bin_idx = np.floor(valid_r / config.dx).astype(int)
    max_bin = int(np.floor(r_max / config.dx))
    bin_idx = np.clip(bin_idx, 0, max_bin - 1)

    count_r = np.bincount(bin_idx, minlength=max_bin)

    azim_mean = np.full((config.nz, max_bin), np.nan)

    # ✅ オンデマンド計算: vorticityをその場で計算
    data_u = data_all_u[t]
    data_v = data_all_v[t]

    # ✅ 共通関数を使用: utils/vorticity.py
    data = calculate_vorticity_z(data_u, data_v, config.dx, config.dy)

    valid_data = data[:, mask]

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for i, b in enumerate(bin_idx): azim_sum[:, b] += valid_data[:, i]
    azim_sum = np.zeros((config.nz, max_bin), dtype=np.float32)
    np.add.at(azim_sum.T, bin_idx, valid_data.T)

    # 割り算（ゼロ割回避）
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r, np.nan)

    # print(f"azim mean data t: {t}, max: {azim_mean.max()}, min: {azim_mean.min()}")
    np.savez(
        os.path.join(folder, f"t{str(t).zfill(3)}.npz"),
        data=azim_mean,
        varname="vorticity_z",
        r_max=r_max,
        dx=config.dx,
        method="azimuthal_mean",
        created_at=datetime.now().isoformat()
    )


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
