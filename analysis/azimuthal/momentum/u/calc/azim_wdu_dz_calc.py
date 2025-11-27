# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_wdu_dz_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid * 1e-3
vgrid = np.loadtxt(config.vgrid_filepath)

output_folder = config.get_data_path("azim", "eq_momentum_u", "wdu_dz")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    data = np.load(os.path.join(config.get_data_path('azim', 'wind_relative_radial'), f"t{str(t).zfill(3)}.npy"))
    data_w = np.load(os.path.join(config.get_data_path('azim', 'ms_w'), f"t{str(t).zfill(3)}.npy"))

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for z in range(config.nz - 1): wdu_dz[z, :] = (data_w[z + 1, :] + data_w[z, :]) * 0.5 * (data[z + 1, :] - data[z, :]) / (vgrid[z + 1] - vgrid[z])
    wdu_dz = (
        (data_w[1:, :] + data_w[:-1, :])
        * 0.5
        * (data[1:, :] - data[:-1, :])
        / (vgrid[1:, np.newaxis] - vgrid[:-1, np.newaxis])
    )
    wdu_dz = wdu_dz.astype(np.float32)

    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), wdu_dz)


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
