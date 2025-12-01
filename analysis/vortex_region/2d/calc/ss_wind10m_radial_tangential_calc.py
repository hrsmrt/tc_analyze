"""Calculate radial and tangential components of 10m wind."""
# python $WORK/tc_analyze/analysis/vortex_region/2d/calc/ss_wind10m_radial_tangential_calc.py
import datetime
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定の初期化
config = AnalysisConfig()
grid = GridHandler(config)

folder1 = config.get_tc_centric_path("vortex_region", "2d/ss_wind10m_radial")
folder2 = config.get_tc_centric_path("vortex_region", "2d/ss_wind10m_tangential")

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

data_all_u = np.memmap(
    f"{config.input_folder}ss_u10m.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)
data_all_v = np.memmap(
    f"{config.input_folder}ss_v10m.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)


def process_t(t):
    """
    Process a single time step to calculate radial and tangential wind components.

    Parameters
    ----------
    t : int
        Time step index
    """
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    # GridHandlerを使って角度を計算
    theta = grid.calculate_theta(cx, cy)
    data_u = data_all_u[t]
    data_v = data_all_v[t]

    v_radial = data_u * np.cos(theta) + data_v * np.sin(theta)
    v_tangential = -data_u * np.sin(theta) + data_v * np.cos(theta)

    np.savez(
        os.path.join(folder1, f"t{str(t).zfill(3)}.npz"),
        data=v_radial,
        created_at=str(datetime.datetime.now()),
        description="Radial component of 10m wind",
    )
    np.savez(
        os.path.join(folder2, f"t{str(t).zfill(3)}.npz"),
        data=v_tangential,
        created_at=str(datetime.datetime.now()),
        description="Tangential component of 10m wind",
    )
    # print(f"t: {t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
