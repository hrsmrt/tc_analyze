"""
流線関数の方位角平均を計算（積分順序2）

✅ ストレージ節約版: オンデマンド計算を使用
方位角平均済みデータを保存せず、元データから直接計算

参考: Smith and Montgomery (2023) 5.61式
はじめz = 0でr方向に積分し、その後はz方向に積分

input: ms_rho.grd, ms_u.grd, ms_v.grd, ms_w.grd, center位置
output: 流線関数

python $WORK/tc_analyze/azim_mean/azim_stream2_calc.py
"""

import os

import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_3d, calculate_azimuthal_mean_relative_wind
from utils.config import AnalysisConfig
from utils.grid import GridHandler, calculate_center_velocity

config = AnalysisConfig()
grid = GridHandler(config)

output_folder = config.get_data_path("azim", "stream2")
os.makedirs(output_folder, exist_ok=True)

vgrid = grid.create_vertical_grid()

center_x_list = config.center_x
center_y_list = config.center_y

# 台風中心の移動速度を計算
center_u_list, center_v_list = calculate_center_velocity(
    center_x_list, center_y_list, config.dt_output
)

# ✅ オンデマンド計算: メモリマップを開く
data_rho = np.memmap(
    f"{config.input_folder}ms_rho.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
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
data_w = np.memmap(
    f"{config.input_folder}ms_w.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算
    rho = calculate_azimuthal_mean_3d(
        data_rho, t, center_x_list, center_y_list, grid
    )
    u, _ = calculate_azimuthal_mean_relative_wind(
        data_u, data_v, t, center_x_list, center_y_list, center_u_list, center_v_list, grid
    )
    w = calculate_azimuthal_mean_3d(
        data_w, t, center_x_list, center_y_list, grid
    )
    # データの形状から半径方向のビン数を取得
    nr = rho.shape[1]
    R = (np.arange(nr) + 0.5) * config.dx
    phi = np.zeros_like(rho, dtype=np.float32)

    # ベクトル化版：r方向の積分（z=0の行）
    # 従来版: for r in range(1, nr): phi[0, r] = phi[0, r - 1] + ...
    dr = np.diff(R)
    integrand_r = 0.5 * (rho[0, 1:] * w[0, 1:] * R[1:] + rho[0, :-1] * w[0, :-1] * R[:-1]) * dr
    phi[0, 1:] = np.cumsum(integrand_r)

    # ベクトル化版：z方向の積分（各r列）
    # 従来版: for z in range(1, config.nz): for r in range(nr): phi[z, r] = phi[z - 1, r] - ...
    dz = np.diff(vgrid)
    integrand_z = -0.5 * (rho[1:, :] + rho[:-1, :]) * 0.5 * (u[1:, :] + u[:-1, :]) * 0.5 * R * dz[:, np.newaxis]
    phi[1:, :] = phi[:1, :] + np.cumsum(integrand_z, axis=0)

    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), phi)
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
