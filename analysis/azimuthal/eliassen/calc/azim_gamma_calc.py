# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_gamma_calc.py
# gamma = (v^2/r + fv)/g

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

output_folder = config.get_data_path("azim", "eliassen", "gamma")
os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    v = np.load(os.path.join(config.get_data_path('azim', 'wind_relative_tangential'), f"t{str(t).zfill(3)}.npy"))
    gamma = (v[:, :] ** 2 / R[:] + f * v[:, :]) / g
    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), gamma)
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
