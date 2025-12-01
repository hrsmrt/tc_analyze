"""
温位の方位角平均を計算して保存

✅ ストレージ節約版: オンデマンド計算を使用
方位角平均済みデータを保存せず、元データから直接計算

input: ms_tem.grd (温度), ms_pres.grd (気圧)
output: 温位 θ = T(Ps/P)^(Rd/Cp)

python $WORK/tc_analyze/azim_mean/azim_theta_calc.py
"""

import os
from datetime import datetime

import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_theta
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

output_folder = config.get_tc_centric_path("azimuthal", "basic/theta")
os.makedirs(output_folder, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く
data_tem = np.memmap(
    f"{config.input_folder}ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_pres = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算
    theta = calculate_azimuthal_mean_theta(
        data_tem, data_pres, t, center_x_list, center_y_list, grid
    )
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=theta,
        varname="theta",
        method="potential_temperature",
        created_at=datetime.now().isoformat()
    )
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
