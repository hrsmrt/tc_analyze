# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_gradient_balance_score_calc.py
import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid

output_folder = config.get_tc_centric_path("azimuthal", "momentum/u/gradient_balance_score")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # 遠心力データの読み込み（.npz優先、.npyフォールバック）
    centrifugal_path = config.get_tc_centric_path('azimuthal', 'momentum/u/centrifugal')
    centrifugal_npz = os.path.join(centrifugal_path, f"t{str(t).zfill(3)}.npz")
    centrifugal_npy = os.path.join(centrifugal_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(centrifugal_npz):
        centrifugal_npz_data = np.load(centrifugal_npz)
        centrifugal = centrifugal_npz_data['data']
    elif os.path.exists(centrifugal_npy):
        centrifugal = np.load(centrifugal_npy)
    else:
        raise FileNotFoundError(f"Neither {centrifugal_npz} nor {centrifugal_npy} found")

    # コリオリ力データの読み込み（.npz優先、.npyフォールバック）
    coriolis_path = config.get_tc_centric_path('azimuthal', 'momentum/u/coriolis')
    coriolis_npz = os.path.join(coriolis_path, f"t{str(t).zfill(3)}.npz")
    coriolis_npy = os.path.join(coriolis_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(coriolis_npz):
        coriolis_npz_data = np.load(coriolis_npz)
        coriolis = coriolis_npz_data['data']
    elif os.path.exists(coriolis_npy):
        coriolis = np.load(coriolis_npy)
    else:
        raise FileNotFoundError(f"Neither {coriolis_npz} nor {coriolis_npy} found")

    # 圧力傾度データの読み込み（.npz優先、.npyフォールバック）
    grad_p_path = config.get_tc_centric_path('azimuthal', 'momentum/u/grad_p')
    grad_p_npz = os.path.join(grad_p_path, f"t{str(t).zfill(3)}.npz")
    grad_p_npy = os.path.join(grad_p_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(grad_p_npz):
        grad_p_npz_data = np.load(grad_p_npz)
        grad_p = grad_p_npz_data['data']
    elif os.path.exists(grad_p_npy):
        grad_p = np.load(grad_p_npy)
    else:
        raise FileNotFoundError(f"Neither {grad_p_npz} nor {grad_p_npy} found")

    gradient_balance_diff = centrifugal[:, 1:-1] + coriolis[:, 1:-1] - grad_p
    score = np.abs(gradient_balance_diff) / (
        np.abs(centrifugal[:, 1:-1])
        + np.abs(coriolis[:, 1:-1])
        + np.abs(grad_p)
        + 1e-10
    )
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=score,
        varname="gradient_balance_score",
        method="gradient_wind_balance_score",
        created_at=datetime.now().isoformat()
    )


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
