"""
ms_dyn_radial_tangential の計算

計算処理を実行します。
"""

# python $WORK/tc_analyze/3d/ms_dyn_radial_tangential_calc.py
import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(config.nx) + 0.5) * config.dx
y = (np.arange(config.ny) + 0.5) * config.dy
grid.X, grid.Y = np.meshgrid(x, y)

folder1 = f"./data/3d/dyn_radial/"
folder2 = f"./data/3d/dyn_tangential/"

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

data_all_u = np.memmap(f"{config.input_folder}/ms_dyn_du.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.nz, config.ny, config.nx))
data_all_v = np.memmap(f"{config.input_folder}/ms_dyn_dv.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.nz, config.ny, config.nx))

def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = grid.X - cx
    dY = grid.Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width
    theta = np.arctan2(dY, dX)

    # (config.nz, config.ny, config.nx) の配列を取得
    data_u = data_all_u[t]  # shape: (config.nz, config.ny, config.nx)
    data_v = data_all_v[t]  # shape: (config.nz, config.ny, config.nx)

    # ブロードキャストで一括計算
    v_radial = data_u * np.cos(theta) + data_v * np.sin(theta)
    v_tangential = -data_u * np.sin(theta) + data_v * np.cos(theta)

    np.save(f"{folder1}/t{str(t).zfill(3)}.npy", v_radial)
    np.save(f"{folder2}/t{str(t).zfill(3)}.npy", v_tangential)

    print(f"t: {t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
