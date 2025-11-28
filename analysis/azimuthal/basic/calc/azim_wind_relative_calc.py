"""
相対風の方位角平均を計算して保存

✅ ストレージ節約版: オンデマンド計算を使用
事前計算された相対風データ (relative_u, relative_v) の保存が不要

✅ 中心移動速度を2次中心差分で自動計算
center_x, center_y から中心の移動速度を導出（config不要）

input: ms_u.grd (東西風), ms_v.grd (南北風), center位置
output: 相対風の方位角平均（動径成分・接線成分）

python $WORK/tc_analyze/azim_mean/azim_wind_relative_calc.py
"""

import os

import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_relative_wind
from utils.basic import calculate_center_velocity
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

output_folder1 = config.get_tc_centric_path("azimuthal", "basic/wind_relative_radial")
output_folder2 = config.get_tc_centric_path("azimuthal", "basic/wind_relative_tangential")

os.makedirs(output_folder1, exist_ok=True)
os.makedirs(output_folder2, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ 台風中心の移動速度を2次中心差分で計算
center_u_list, center_v_list = calculate_center_velocity(
    center_x_list, center_y_list, config.dt_output
)

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
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    azim_mean_radial, azim_mean_tangential = calculate_azimuthal_mean_relative_wind(
        data_u, data_v, t, center_x_list, center_y_list, center_u_list, center_v_list, grid
    )

    print(
        f"azim mean data t: {t}, radial max: {azim_mean_radial.max():.2f}, min: {azim_mean_radial.min():.2f}"
    )
    np.save(os.path.join(output_folder1, f"t{str(t).zfill(3)}.npy"), azim_mean_radial)

    print(
        f"azim mean data t: {t}, tangential max: {azim_mean_tangential.max():.2f}, min: {azim_mean_tangential.min():.2f}"
    )
    np.save(os.path.join(output_folder2, f"t{str(t).zfill(3)}.npy"), azim_mean_tangential)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
