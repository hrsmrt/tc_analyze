# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_xi_calc.py
# output: xi = 2v/r + f

import os

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

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/xi")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    v = np.load(os.path.join(config.get_tc_centric_path('azimuthal', 'basic/wind_relative_tangential'), f"t{str(t).zfill(3)}.npy"))
    xi = 2 * v / R + f
    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), xi)
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
