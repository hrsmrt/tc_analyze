# python $WORK/tc_analyze/analysis/azimuthal/basic/calc/azim_wind10m_tangential_max_calc.py
import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

time_list = config.time_list

folder = config.get_tc_centric_path("azimuthal", "basic/wind10m_tangential")

os.makedirs(folder, exist_ok=True)


# メインループ
def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    npz_path = os.path.join(folder, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(folder, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

    return data.max(), data.argmax() * config.dx


max_values = Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)

max_values = np.array(max_values)

wind10m_tangential_max = max_values[:, 0]
wind10m_tangential_rmw = max_values[:, 1]

np.savez(
    os.path.join(folder, "wind10m_tangential_max.npz"),
    data=wind10m_tangential_max,
    varname="wind10m_tangential_max",
    method="maximum_value",
    created_at=datetime.now().isoformat()
)
np.savez(
    os.path.join(folder, "wind10m_tangential_rmw.npz"),
    data=wind10m_tangential_rmw,
    varname="wind10m_tangential_rmw",
    method="radius_of_maximum_wind",
    created_at=datetime.now().isoformat()
)
