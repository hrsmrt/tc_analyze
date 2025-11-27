# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_gradient_wind_eq_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid

output_folder = config.get_data_path("azim", "eq_momentum_u", "gradient_wind_eq")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    centrifugal = np.load(
        os.path.join(config.get_data_path('azim', 'eq_momentum_u', 'centrifugal'), f"t{str(t).zfill(3)}.npy")
    )
    coriolis = np.load(os.path.join(config.get_data_path('azim', 'eq_momentum_u', 'coriolis'), f"t{str(t).zfill(3)}.npy"))
    grad_p = np.load(os.path.join(config.get_data_path('azim', 'eq_momentum_u', 'grad_p'), f"t{str(t).zfill(3)}.npy"))
    gradient_wind_eq = centrifugal[:, 1:-1] + coriolis[:, 1:-1] - grad_p
    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), gradient_wind_eq)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
