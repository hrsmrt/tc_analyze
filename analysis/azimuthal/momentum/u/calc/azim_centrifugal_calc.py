# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/calc/azim_centrifugal_calc.py
import os
from datetime import datetime

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
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path('azimuthal', 'basic/wind_relative_tangential')
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for r in range(nr): centrifugal[:, r] = -(data[:, r]**2) / rgrid[r]
    centrifugal = -(data**2) / rgrid[np.newaxis, :]
    centrifugal = centrifugal.astype(np.float32)

    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=centrifugal,
        varname="centrifugal",
        method="centrifugal_force",
        created_at=datetime.now().isoformat()
    )


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
