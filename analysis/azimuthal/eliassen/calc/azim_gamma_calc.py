# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_gamma_calc.py
# gamma = (v^2/r + fv)/g

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

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/gamma")
os.makedirs(output_folder, exist_ok=True)


def process_t(t):
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

    gamma = (v[:, :] ** 2 / R[:] + f * v[:, :]) / g
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=gamma,
        varname="gamma",
        method="eliassen_centrifugal_parameter",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
