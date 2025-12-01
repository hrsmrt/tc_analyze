# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_wdu_dz_calc.py
import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid * 1e-3
vgrid = np.loadtxt(config.vgrid_filepath)

output_folder = config.get_tc_centric_path("azimuthal", "momentum/u/wdu_dz")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # 動径風速データの読み込み（.npz優先、.npyフォールバック）
    u_path = config.get_tc_centric_path('azimuthal', 'basic/wind_relative_radial')
    u_npz = os.path.join(u_path, f"t{str(t).zfill(3)}.npz")
    u_npy = os.path.join(u_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(u_npz):
        u_npz_data = np.load(u_npz)
        data = u_npz_data['data']
    elif os.path.exists(u_npy):
        data = np.load(u_npy)
    else:
        raise FileNotFoundError(f"Neither {u_npz} nor {u_npy} found")

    # 鉛直風速データの読み込み（.npz優先、.npyフォールバック）
    w_path = config.get_tc_centric_path('azimuthal', 'basic/ms_w')
    w_npz = os.path.join(w_path, f"t{str(t).zfill(3)}.npz")
    w_npy = os.path.join(w_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(w_npz):
        w_npz_data = np.load(w_npz)
        data_w = w_npz_data['data']
    elif os.path.exists(w_npy):
        data_w = np.load(w_npy)
    else:
        raise FileNotFoundError(f"Neither {w_npz} nor {w_npy} found")

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for z in range(config.nz - 1): wdu_dz[z, :] = (data_w[z + 1, :] + data_w[z, :]) * 0.5 * (data[z + 1, :] - data[z, :]) / (vgrid[z + 1] - vgrid[z])
    wdu_dz = (
        (data_w[1:, :] + data_w[:-1, :])
        * 0.5
        * (data[1:, :] - data[:-1, :])
        / (vgrid[1:, np.newaxis] - vgrid[:-1, np.newaxis])
    )
    wdu_dz = wdu_dz.astype(np.float32)

    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=wdu_dz,
        varname="wdu_dz",
        method="vertical_momentum_advection",
        created_at=datetime.now().isoformat()
    )


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
