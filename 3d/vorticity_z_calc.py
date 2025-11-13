"""
vorticity_z の計算

計算処理を実行します。
"""

# python $WORK/tc_analyze/3d/vorticity_z_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

# 設定とグリッドの初期化
config = AnalysisConfig()

FOLDER = "./data/3d/vorticity_z/"

os.makedirs(FOLDER, exist_ok=True)

data_all_u = np.memmap(
    f"{config.input_folder}/ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_all_v = np.memmap(
    f"{config.input_folder}/ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    """指定された時刻tのz方向渦度を計算する"""
    # (config.nz, config.ny, config.nx) の配列を取得
    data_u = data_all_u[t]  # shape: (config.nz, config.ny, config.nx)
    data_v = data_all_v[t]  # shape: (config.nz, config.ny, config.nx)

    vor = np.zeros((config.nz, config.ny, config.nx), dtype=np.float32)
    for z in range(config.nz):
        dv_dx = (np.roll(data_v[z], -1, axis=1) - np.roll(data_v[z], 1, axis=1)) / (
            2 * config.dx
        )
        du_dy = (np.roll(data_u[z], -1, axis=0) - np.roll(data_u[z], 1, axis=0)) / (
            2 * config.dy
        )
        du_dy[0, : config.nx // 2] = (
            data_u[z, 1, : config.nx // 2] - data_u[z, -1, config.nx // 2:]
        ) / (2 * config.dy)
        du_dy[0, config.nx // 2:] = (
            data_u[z, 1, config.nx // 2:] - data_u[z, -1, : config.nx // 2]
        ) / (2 * config.dy)
        du_dy[-1, : config.nx // 2] = (
            data_u[z, 0, : config.nx // 2] - data_u[z, -2, config.nx // 2:]
        ) / (2 * config.dy)
        du_dy[-1, config.nx // 2:] = (
            data_u[z, 0, config.nx // 2:] - data_u[z, -2, : config.nx // 2]
        ) / (2 * config.dy)
        vor[z] = dv_dx - du_dy
    np.save(f"{FOLDER}vor_t{str(t).zfill(3)}.npy", vor)
    print(f"t: {t} vorticity calc done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
