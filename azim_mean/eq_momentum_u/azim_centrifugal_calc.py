# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_centrifugal_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

radius = 1000e3

nr = int(radius / config.dx)

rgrid = grid.create_radial_grid(radius)

output_folder = "./data/azim/eq_momentum_u/centrifugal/"

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    data = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")
    centrifugal = -(data**2)
    for r in range(nr):
        centrifugal[:, r] = centrifugal[:, r] / (rgrid[r])
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", centrifugal)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
