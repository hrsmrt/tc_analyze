# python $WORK/tc_analyze/azim_mean/azim_momentum_calc.py
# input: f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy"
# output: 単位質量あたりの角運動量 M = rv + f r^2/2

import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig

config = AnalysisConfig()

time_list = config.time_list

r_max = 1000e3

nr = int(r_max / config.dx)
R = (np.arange(nr) + 0.5) * config.dx
f = config.f

output_folder = "./data/azim/momentum/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    u_tangential = np.load(f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy")
    M = R * u_tangential + 0.5 * f * R**2
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", M)
    print(f"t={t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
