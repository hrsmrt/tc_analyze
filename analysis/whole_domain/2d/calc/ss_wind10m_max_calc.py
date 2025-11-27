"""Calculate maximum 10m wind speed at each time step."""
# python $WORK/tc_analyze/analysis/whole_domain/2d/plot/ss_wind10m_max_calc.py
import os

import numpy as np

from utils.config import AnalysisConfig

# 設定の初期化
config = AnalysisConfig()
output_folder = config.get_data_path()
os.makedirs(output_folder, exist_ok=True)

ss_u10m = np.fromfile(f"{config.input_folder}ss_u10m.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)
ss_v10m = np.fromfile(f"{config.input_folder}ss_v10m.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)

data_abs = np.sqrt(ss_v10m**2 + ss_u10m**2)
data_abs_max = data_abs.max(axis=(1, 2))

np.save(os.path.join(output_folder, "ss_wind10m_max.npy"), data_abs_max)
