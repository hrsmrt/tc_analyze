# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_R_calc.py
# output: R = r \rho \theta

import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.basic import PRES_S, Rd, Cp, Lv, g
from utils.config import AnalysisConfig

config = AnalysisConfig()

r_max = 1000e3

nr = int(r_max / config.dx)
R = (np.arange(nr) + 0.5) * config.dx

# エイリアス（コードの変更を最小限にするため）
f = config.f
pres_s = PRES_S
L = Lv

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/R")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    # Load rho data (.npz優先、.npyフォールバック)
    rho_path = config.get_tc_centric_path('azimuthal', 'basic/ms_rho')
    rho_npz = os.path.join(rho_path, f"t{str(t).zfill(3)}.npz")
    rho_npy = os.path.join(rho_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(rho_npz):
        rho_data = np.load(rho_npz)
        rho = rho_data['data']
    elif os.path.exists(rho_npy):
        rho = np.load(rho_npy)
    else:
        raise FileNotFoundError(f"Neither {rho_npz} nor {rho_npy} found")

    # Load theta data (.npz優先、.npyフォールバック)
    theta_path = config.get_tc_centric_path('azimuthal', 'basic/theta')
    theta_npz = os.path.join(theta_path, f"t{str(t).zfill(3)}.npz")
    theta_npy = os.path.join(theta_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(theta_npz):
        theta_data = np.load(theta_npz)
        theta = theta_data['data']
    elif os.path.exists(theta_npy):
        theta = np.load(theta_npy)
    else:
        raise FileNotFoundError(f"Neither {theta_npz} nor {theta_npy} found")

    R_eliassen = R * rho * theta
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=R_eliassen,
        varname="R",
        method="eliassen_R_parameter",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
