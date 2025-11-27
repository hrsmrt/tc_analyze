# python $WORK/tc_analyze/azim_mean/eliassen/azim_I2_calc.py
# output: I^2 = \xi (dv/dr + v/r * f)

import os

import numpy as np
from joblib import Parallel, delayed

from utils.basic import PRES_S, Rd, Cp, Lv, g0
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
g = g0

output_folder = config.get_data_path("azim", "eliassen", "I2")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    xi = np.load(os.path.join(config.get_data_path('azim', 'eliassen'), f"xi/t{str(t).zfill(3)}.npy"))
    v = np.load(os.path.join(config.get_data_path('azim', 'wind_relative_tangential'), f"t{str(t).zfill(3)}.npy"))
    dv_dr = (v[:, 1:] - v[:, :-1]) / config.dx
    I2 = (
        (xi[:, 1:] + xi[:, :-1])
        / 2
        * (dv_dr + (v[:, 1:] + v[:, :-1]) / (2 * R_wall) + f)
    )
    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), I2)
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
