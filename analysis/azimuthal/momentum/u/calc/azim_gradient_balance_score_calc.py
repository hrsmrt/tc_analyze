# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_gradient_balance_score_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid

output_folder = config.get_data_path("azim", "eq_momentum_u", "gradient_balance_score")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    centrifugal = np.load(
        os.path.join(config.get_data_path('azim', 'eq_momentum_u', 'centrifugal'), f"t{str(t).zfill(3)}.npy")
    )
    coriolis = np.load(os.path.join(config.get_data_path('azim', 'eq_momentum_u', 'coriolis'), f"t{str(t).zfill(3)}.npy"))
    grad_p = np.load(os.path.join(config.get_data_path('azim', 'eq_momentum_u', 'grad_p'), f"t{str(t).zfill(3)}.npy"))
    gradient_balance_diff = centrifugal[:, 1:-1] + coriolis[:, 1:-1] - grad_p
    score = np.abs(gradient_balance_diff) / (
        np.abs(centrifugal[:, 1:-1])
        + np.abs(coriolis[:, 1:-1])
        + np.abs(grad_p)
        + 1e-10
    )
    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), score)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
