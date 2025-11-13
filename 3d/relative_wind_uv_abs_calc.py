"""
relative_wind_uv_abs の計算

計算処理を実行します。
"""

# python $WORK/tc_analyze/3d/relative_wind_uv_abs_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

R_MAX = 1000e3

# 格子点座標（m単位）
x = (np.arange(config.nx) + 0.5) * config.dx
y = (np.arange(config.ny) + 0.5) * config.dy
grid.X, grid.Y = np.meshgrid(x, y)

OUTPUT_FOLDER = "./data/3d/relative_wind_uv_abs/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

center_x_list = config.center_x
center_y_list = config.center_y


def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = grid.X - cx
    dY = grid.Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width
    np.arctan2(dY, dX)

    # (config.nz, config.ny, config.nx) の配列を取得
    data_u = np.load(
        f"./data/3d/relative_u/t{str(t).zfill(3)}.npy"
    )  # shape: (config.nz, config.ny, config.nx)
    data_v = np.load(
        f"./data/3d/relative_v/t{str(t).zfill(3)}.npy"
    )  # shape: (config.nz, config.ny, config.nx)

    # ブロードキャストで一括計算
    v_abs = np.sqrt(data_u**2 + data_v**2)

    np.save(f"{OUTPUT_FOLDER}/t{str(t).zfill(3)}.npy", v_abs)

    print(f"t: {t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
