# python $WORK/tc_analyze/azim_mean/azim_stream2_calc.py
# output: 流線関数
# 参考: Smith and Montgomery (2023) 5.61式
# はじめz = 0でr方向に積分し、その後はz方向に積分

import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

output_folder = config.get_data_path("azim", "stream2")
os.makedirs(output_folder, exist_ok=True)

vgrid = grid.create_vertical_grid()


def process_t(t):
    rho = np.load(os.path.join(config.get_data_path('azim', 'ms_rho'), f"t{str(t).zfill(3)}.npy"))
    u = np.load(os.path.join(config.get_data_path('azim', 'wind_relative_radial'), f"t{str(t).zfill(3)}.npy"))
    w = np.load(os.path.join(config.get_data_path('azim', 'ms_w'), f"t{str(t).zfill(3)}.npy"))
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
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
