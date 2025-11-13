"""
theta_e の計算

計算処理を実行します。
"""

# python $WORK/tc_analyze/3d/theta_e_calc.py
# output: 相当温位 θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))

import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

# 設定読み込み
config = AnalysisConfig()

R_MAX = 1000e3

NR = int(R_MAX / config.dx)
CORIOLIS_PARAM = 3.77468e-5

OUTPUT_FOLDER = "./data/3d/theta_e/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PRES_S = 100000  # 基準気圧 Pa
RD = 287.05  # 気体定数 J/(kg·K)
CP = 1005  # 定圧比熱 J/(kg·K)
L = 2.5e6  # 蒸発潜熱 J/kg

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
    """指定された時刻tの相当温位を計算する"""
    tem = data_tem[t]
    pres = data_pres[t]
    qv = data_qv[t]
    rv = qv / (1 - qv)
    theta_e = tem * (PRES_S / pres) ** (RD / CP) * np.exp(L * rv / (CP * tem))
    np.save(f"{OUTPUT_FOLDER}t{str(t).zfill(3)}.npy", theta_e)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
