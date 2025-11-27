"""
相当温位の方位角平均を計算して保存

✅ ストレージ節約版: オンデマンド計算を使用
方位角平均済みデータを保存せず、元データから直接計算

input: ms_tem.grd (温度), ms_pres.grd (気圧), ms_qv.grd (比湿)
output: 相当温位 θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))

python $WORK/tc_analyze/azim_mean/azim_theta_e_calc.py
"""

import os

import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_theta_e
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

OUTPUT_FOLDER = config.get_data_path("azim", "theta_e")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
data_qv = np.memmap(
    f"{config.input_folder}ms_qv.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算
    theta_e = calculate_azimuthal_mean_theta_e(
        data_tem, data_pres, data_qv, t, center_x_list, center_y_list, grid
    )
    np.save(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.npy"), theta_e)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
