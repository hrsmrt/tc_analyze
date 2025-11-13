# python $WORK/tc_analyze/azim_mean/eliassen/azim_I2_calc.py
# output: I^2 = \xi (dv/dr + v/r * f)

import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

nr = int(np.floor(r_max / config.dx))
R = (np.arange(nr) + 0.5) * config.dx
R_wall = (np.arange(1, nr)) * config.dx
f = 3.77468e-5

output_folder = "./data/azim/eliassen/I2/"
os.makedirs(output_folder, exist_ok=True)

pres_s = 100000  # 基準気圧 Pa
Rd = 287.05  # 気体定数 J/(kg·K)
Cp = 1005  # 定圧比熱 J/(kg·K)
L = 2.5e6  # 蒸発潜熱 J/kg

theta_ref = 300.0  # 基準温位 K

g = 9.80665


def process_t(t):
    xi = np.load(f"./data/azim/eliassen/xi/t{str(t).zfill(3)}.npy")
    v = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")
    dv_dr = (v[:, 1:] - v[:, :-1]) / config.dx
    I2 = (
        (xi[:, 1:] + xi[:, :-1])
        / 2
        * (dv_dr + (v[:, 1:] + v[:, :-1]) / (2 * R_wall) + f)
    )
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", I2)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
