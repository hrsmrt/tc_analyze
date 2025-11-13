# python $WORK/tc_analyze/azim_mean/azim_momentum_calc.py
# input: f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy"
# output: 単位質量あたりの角運動量 M = rv + f r^2/2

import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

CORIOLIS_PARAM = config.f

OUTPUT_FOLDER = "./data/azim/momentum/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_t(t):
    u_tangential = np.load(f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy")
    # データの形状から半径方向のビン数を取得
    nr = u_tangential.shape[1]
    rgrid = (np.arange(nr) + 0.5) * config.dx
    momentum = rgrid * u_tangential + 0.5 * CORIOLIS_PARAM * rgrid**2
    np.save(f"{OUTPUT_FOLDER}t{str(t).zfill(3)}.npy", momentum)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
