# python $WORK/tc_analyze/azim_mean/azim_theta_e_calc.py
# input: os.path.join(config.get_data_path('azim', 'ms_tem'), f"t{str(t).zfill(3)}.npy") 温度
# input: os.path.join(config.get_data_path('azim', 'ms_pres'), f"t{str(t).zfill(3)}.npy") 気圧
# input: os.path.join(config.get_data_path('azim', 'ms_qv'), f"t{str(t).zfill(3)}.npy") 比湿
# output: 相当温位 θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))

import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

OUTPUT_FOLDER = config.get_data_path("azim", "theta_e")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 物理定数
PRES_SURFACE = 100000  # 基準気圧 Pa
GAS_CONST_DRY = 287.05  # 乾燥大気の気体定数 J/(kg·K)
HEAT_CAPACITY = 1005  # 定圧比熱 J/(kg·K)
LATENT_HEAT = 2.5e6  # 蒸発潜熱 J/kg


def process_t(t):
    temperature = np.load(os.path.join(config.get_data_path('azim', 'ms_tem'), f"t{str(t).zfill(3)}.npy"))
    pressure = np.load(os.path.join(config.get_data_path('azim', 'ms_pres'), f"t{str(t).zfill(3)}.npy"))
    specific_humidity = np.load(os.path.join(config.get_data_path('azim', 'ms_qv'), f"t{str(t).zfill(3)}.npy"))
    mixing_ratio = specific_humidity / (1 - specific_humidity)
    theta_e = (
        temperature
        * (PRES_SURFACE / pressure) ** (GAS_CONST_DRY / HEAT_CAPACITY)
        * np.exp(LATENT_HEAT * mixing_ratio / (HEAT_CAPACITY * temperature))
    )
    np.save(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.npy"), theta_e)
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
