# python $WORK/tc_analyze/2d/ss_slp_min_calc.py
import os

import numpy as np

from utils.config import AnalysisConfig

# 設定の初期化
config = AnalysisConfig()
output_folder = "./data/"
os.makedirs(output_folder, exist_ok=True)

data = np.fromfile(f"{config.input_folder}ss_slp.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)
data_min = data.min(axis=(1, 2))
np.save(f"{output_folder}ss_slp_min.npy", data_min)
