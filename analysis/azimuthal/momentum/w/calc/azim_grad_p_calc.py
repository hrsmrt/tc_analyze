# python $WORK/tc_analyze/analysis/azimuthal/momentum/w/calc/azim_grad_p_calc.py
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

output_folder = config.get_tc_centric_path("azimuthal", "momentum/w/grad_p")

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

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for z in range(config.nz - 1): grad_p[z, :] = 1 / ((data_rho[z + 1, :] + data_rho[z, :]) * 0.5) * (data[z + 1, :] - data[z, :]) / (vgrid[z + 1] - vgrid[z]) + 9.80665
    grad_p = (
        1
        / ((data_rho[1:, :] + data_rho[:-1, :]) * 0.5)
        * (data[1:, :] - data[:-1, :])
        / (vgrid[1:, np.newaxis] - vgrid[:-1, np.newaxis])
        + 9.80665
    )
    grad_p = grad_p.astype(np.float32)

    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=grad_p,
        varname="grad_p",
        method="vertical_pressure_gradient",
        created_at=datetime.now().isoformat()
    )


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
