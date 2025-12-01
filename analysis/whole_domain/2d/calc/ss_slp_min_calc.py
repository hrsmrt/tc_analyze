"""Calculate minimum sea level pressure at each time step."""
# python $WORK/tc_analyze/analysis/whole_domain/2d/plot/ss_slp_min_calc.py
import datetime
import os

import numpy as np

from utils.config import AnalysisConfig

# 設定の初期化
config = AnalysisConfig()
output_folder = config.get_domain_path("whole_domain", "2d/ss_slp_min")
os.makedirs(output_folder, exist_ok=True)

data = np.fromfile(f"{config.input_folder}ss_slp.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)
data_min = data.min(axis=(1, 2))
np.savez(
    os.path.join(output_folder, "ss_slp_min.npz"),
    data=data_min,
    timestamp=datetime.datetime.now().isoformat(),
    description="Minimum sea level pressure at each time step",
)
print(f"Saved: {output_folder}/ss_slp_min.npz")
