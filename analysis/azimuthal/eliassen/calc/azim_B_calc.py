# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_B_calc.py
# input: os.path.join(config.get_tc_centric_path('azimuthal', 'basic/buoyancy'), f"t{str(t).zfill(3)}.npy") 温度
# output: B = db/dr

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

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/B")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    # Load buoyancy data (.npz優先、.npyフォールバック)
    b_path = config.get_tc_centric_path('azimuthal', 'eliassen/buoyancy')
    b_npz = os.path.join(b_path, f"t{str(t).zfill(3)}.npz")
    b_npy = os.path.join(b_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(b_npz):
        b_data = np.load(b_npz)
        b = b_data['data']
    elif os.path.exists(b_npy):
        b = np.load(b_npy)
    else:
        raise FileNotFoundError(f"Neither {b_npz} nor {b_npy} found")

    db_dr = (b[:, 1:] - b[:, :-1]) / config.dx
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=db_dr,
        varname="B",
        method="eliassen_buoyancy_radial_gradient",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
