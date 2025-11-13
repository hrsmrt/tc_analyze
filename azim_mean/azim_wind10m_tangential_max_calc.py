# python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_max_calc.py
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

time_list = config.time_list

folder = f"./data/azim/wind10m_tangential/"

os.makedirs(folder, exist_ok=True)


# メインループ
def process_t(t):
    # データの読み込み
    data = np.load(f"{folder}t{str(t).zfill(3)}.npy")
    return data.max(), data.argmax() * config.dx


max_values = Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)

max_values = np.array(max_values)

wind10m_tangential_max = max_values[:, 0]
wind10m_tangential_rmw = max_values[:, 1]

np.save(f"{folder}wind10m_tangential_max.npy", wind10m_tangential_max)
np.save(f"{folder}wind10m_tangential_rmw.npy", wind10m_tangential_rmw)
