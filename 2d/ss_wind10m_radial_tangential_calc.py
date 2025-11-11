# python $WORK/tc_analyze/analyze/2d/ss_wind10m_radial_tangential_calc.py
import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定の初期化
config = AnalysisConfig()
grid = GridHandler(config)

folder1 = f"./data/2d/wind10m_radial/"
folder2 = f"./data/2d/wind10m_tangential/"

os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

data_all_u = np.memmap(f"{config.input_folder}ss_u10m.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.ny, config.nx))
data_all_v = np.memmap(f"{config.input_folder}ss_v10m.grd", dtype=">f4", mode="r",
                    shape=(config.nt, config.ny, config.nx))

def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    # GridHandlerを使って角度を計算
    theta = grid.calculate_theta(cx, cy)
    data_u = data_all_u[t]
    data_v = data_all_v[t]

    v_radial = data_u * np.cos(theta) + data_v * np.sin(theta)
    v_tangential = -data_u * np.sin(theta) + data_v * np.cos(theta)

    np.save(f"{folder1}t{str(t).zfill(3)}.npy", v_radial)
    np.save(f"{folder2}t{str(t).zfill(3)}.npy", v_tangential)
    print(f"t: {t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
