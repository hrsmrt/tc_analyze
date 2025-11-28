# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_centrifugal_calc.py
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

output_folder = config.get_tc_centric_path("azimuthal", "momentum/u/centrifugal")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    data = np.load(os.path.join(config.get_tc_centric_path('azimuthal', 'basic/wind_relative_tangential'), f"t{str(t).zfill(3)}.npy"))

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for r in range(nr): centrifugal[:, r] = -(data[:, r]**2) / rgrid[r]
    centrifugal = -(data**2) / rgrid[np.newaxis, :]
    centrifugal = centrifugal.astype(np.float32)

    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), centrifugal)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
