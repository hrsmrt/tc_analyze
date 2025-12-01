# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_buoyancy_calc.py
# input: os.path.join(config.get_tc_centric_path('azimuthal', 'basic/theta'), f"t{str(t).zfill(3)}.npy") 温度
# output: 浮力 b = g ln(θ/θ_ref)

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

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/buoyancy")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
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

    b = g * np.log(theta / theta_ref)
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=b,
        varname="buoyancy",
        method="eliassen_buoyancy",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
