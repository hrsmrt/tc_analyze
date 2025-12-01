# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_grad_p_calc.py
import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid * 1e-3

output_folder = config.get_tc_centric_path("azimuthal", "momentum/u/grad_p")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # 圧力データの読み込み（.npz優先、.npyフォールバック）
    pres_path = config.get_tc_centric_path('azimuthal', 'basic/ms_pres')
    pres_npz = os.path.join(pres_path, f"t{str(t).zfill(3)}.npz")
    pres_npy = os.path.join(pres_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(pres_npz):
        pres_npz_data = np.load(pres_npz)
        data = pres_npz_data['data']
    elif os.path.exists(pres_npy):
        data = np.load(pres_npy)
    else:
        raise FileNotFoundError(f"Neither {pres_npz} nor {pres_npy} found")

    # 密度データの読み込み（.npz優先、.npyフォールバック）
    rho_path = config.get_tc_centric_path('azimuthal', 'basic/ms_rho')
    rho_npz = os.path.join(rho_path, f"t{str(t).zfill(3)}.npz")
    rho_npy = os.path.join(rho_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(rho_npz):
        rho_npz_data = np.load(rho_npz)
        data_rho = rho_npz_data['data']
    elif os.path.exists(rho_npy):
        data_rho = np.load(rho_npy)
    else:
        raise FileNotFoundError(f"Neither {rho_npz} nor {rho_npy} found")

    grad_p = -1 / data_rho[:, 1:-1] * (data[:, 2:] - data[:, :-2]) / (config.dx * 2)
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=grad_p,
        varname="grad_p",
        method="radial_pressure_gradient",
        created_at=datetime.now().isoformat()
    )


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
