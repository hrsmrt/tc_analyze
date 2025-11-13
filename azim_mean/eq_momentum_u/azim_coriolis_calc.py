# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_coriolis_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

f = 3.77468e-05  # コリオリパラメータ

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid

output_folder = "./data/azim/eq_momentum_u/coriolis/"

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    data = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")
    coriolis = -data * f
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", coriolis)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
