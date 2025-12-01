"""
流線関数の方位角平均を計算

✅ ストレージ節約版: オンデマンド計算を使用
方位角平均済みデータを保存せず、元データから直接計算

参考: Smith and Montgomery (2023) 5.61式
はじめr = 0でz方向に積分し、その後はr方向に積分

input: ms_rho.grd, ms_u.grd, ms_v.grd, ms_w.grd, center位置
output: 流線関数

python $WORK/tc_analyze/azim_mean/azim_stream_calc.py
"""

import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_3d, calculate_azimuthal_mean_relative_wind
from utils.basic import calculate_center_velocity
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

vgrid = grid.create_vertical_grid()

output_folder = config.get_tc_centric_path("azimuthal", "basic/stream")
os.makedirs(output_folder, exist_ok=True)

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

    # ベクトル化版：z方向の積分（r=0の列）
    # 従来版: for z in range(1, config.nz): phi[z, 0] = phi[z - 1, 0] - ...
    dz = np.diff(vgrid)
    integrand_z = -0.5 * (rho[1:, 0] * u[1:, 0] + rho[:-1, 0] * u[:-1, 0]) * R[0] * dz
    phi[1:, 0] = np.cumsum(integrand_z)

    # ベクトル化版：r方向の積分（各z層）
    # 従来版: for z in range(config.nz): for r in range(1, nr): phi[z, r] = phi[z, r - 1] + ...
    dr = np.diff(R)
    integrand_r = 0.5 * (rho[:, 1:] * w[:, 1:] * R[1:] + rho[:, :-1] * w[:, :-1] * R[:-1]) * dr
    phi[:, 1:] = phi[:, :1] + np.cumsum(integrand_r, axis=1)

    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=phi,
        varname="stream_function",
        method="meridional_streamfunction",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
