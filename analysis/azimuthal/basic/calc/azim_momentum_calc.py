"""
角運動量の方位角平均を計算して保存

✅ ストレージ節約版: オンデマンド計算を使用
方位角平均済みデータを保存せず、元データから直接計算

input: ms_u.grd (東西風), ms_v.grd (南北風)
output: 単位質量あたりの角運動量 M = rv + f r^2/2

python $WORK/tc_analyze/azim_mean/azim_momentum_calc.py
"""

import os

import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_momentum, calculate_azimuthal_mean_wind
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

OUTPUT_FOLDER = config.get_data_path("azim", "momentum")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く
data_u = np.memmap(
    f"{config.input_folder}ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_v = np.memmap(
    f"{config.input_folder}ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算
    # まず接線風の方位角平均を計算
    _, azim_tangential = calculate_azimuthal_mean_wind(
        data_u, data_v, t, center_x_list, center_y_list, grid
    )
    # 接線風から角運動量を計算
    momentum = calculate_azimuthal_mean_momentum(azim_tangential, config)
    np.save(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.npy"), momentum)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
