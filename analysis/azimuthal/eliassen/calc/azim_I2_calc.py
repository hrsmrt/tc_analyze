# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_I2_calc.py
# output: I^2 = \xi (dv/dr + v/r * f)

import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.basic import PRES_S, Rd, Cp, Lv, g
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

nr = int(np.floor(r_max / config.dx))
R = (np.arange(nr) + 0.5) * config.dx
R_wall = (np.arange(1, nr)) * config.dx

# エイリアス（コードの変更を最小限にするため）
f = config.f
pres_s = PRES_S
L = Lv

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/I2")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    # Load xi data (.npz優先、.npyフォールバック)
    xi_path = config.get_tc_centric_path('azimuthal', 'eliassen/xi')
    xi_npz = os.path.join(xi_path, f"t{str(t).zfill(3)}.npz")
    xi_npy = os.path.join(xi_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(xi_npz):
        xi_data = np.load(xi_npz)
        xi = xi_data['data']
    elif os.path.exists(xi_npy):
        xi = np.load(xi_npy)
    else:
        raise FileNotFoundError(f"Neither {xi_npz} nor {xi_npy} found")

    # Load v data (.npz優先、.npyフォールバック)
    v_path = config.get_tc_centric_path('azimuthal', 'basic/wind_relative_tangential')
    v_npz = os.path.join(v_path, f"t{str(t).zfill(3)}.npz")
    v_npy = os.path.join(v_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(v_npz):
        v_data = np.load(v_npz)
        v = v_data['data']
    elif os.path.exists(v_npy):
        v = np.load(v_npy)
    else:
        raise FileNotFoundError(f"Neither {v_npz} nor {v_npy} found")
    dv_dr = (v[:, 1:] - v[:, :-1]) / config.dx
    I2 = (
        (xi[:, 1:] + xi[:, :-1])
        / 2
        * (dv_dr + (v[:, 1:] + v[:, :-1]) / (2 * R_wall) + f)
    )
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=I2,
        varname="I2",
        method="eliassen_inertial_parameter",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
