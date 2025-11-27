# python $WORK/tc_analyze/azim_mean/azim_stream_calc.py
# output: 流線関数
# 参考: Smith and Montgomery (2023) 5.61式
# はじめr = 0でz方向に積分し、その後はr方向に積分

import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

vgrid = grid.create_vertical_grid()

output_folder = config.get_data_path("azim", "stream")
os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    rho = np.load(f"{config.get_data_path('azim', 'ms_rho')}/t{str(t).zfill(3)}.npy")
    u = np.load(f"{config.get_data_path('azim', 'wind_relative_radial')}/t{str(t).zfill(3)}.npy")
    w = np.load(f"{config.get_data_path('azim', 'ms_w')}/t{str(t).zfill(3)}.npy")
    # データの形状から半径方向のビン数を取得
    nr = rho.shape[1]
    R = (np.arange(nr) + 0.5) * config.dx
    phi = np.zeros_like(rho)

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

    np.save(f"{output_folder}/t{str(t).zfill(3)}.npy", phi)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
