# python $WORK/tc_analyze/z_profile/hf_calc.py
# hf: moist static energy, Nolan+2007 (3)式

import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

# 定数
cp = 1004 # J/kg/K
L = 2.5e6 # J/kg, An introduction to clouds, Table 2.1(温度依存性あり)
Lv = 2.8e6 # J/kg, An introduction to clouds, Table 2.1(温度依存性あり)
g = 9.81 # m/s

# 出力ディレクトリ
output_dir = "./data/z_profile/"
os.makedirs(output_dir, exist_ok=True)

# 鉛直グリッドの読み込み
vgrid = np.loadtxt(config.vgrid_filepath)

# データファイルの準備
files = {
    "tem": np.memmap(f"{config.input_folder}ms_tem.grd", dtype=">f4", mode="r", shape=(config.nt, config.nz, config.ny, config.nx)),
    "qv": np.memmap(f"{config.input_folder}ms_qv.grd", dtype=">f4", mode="r", shape=(config.nt, config.nz, config.ny, config.nx)),
    "qg": np.memmap(f"{config.input_folder}ms_qg.grd", dtype=">f4", mode="r", shape=(config.nt, config.nz, config.ny, config.nx)),
}

def hf_t(t):
    T  = files["tem"][t].mean(axis=(1,2))
    qv = files["qv"][t].mean(axis=(1,2))
    qg = files["qg"][t].mean(axis=(1,2))

    hf = cp * T + g * vgrid + L * qv + Lv * qg
    return hf

hf_all = Parallel(n_jobs=config.n_jobs)(delayed(hf_t)(t) for t in range(config.t_first, config.t_last))

hf_all = np.array(hf_all)
np.save(f"{output_dir}hf.npy", hf_all)
print(f"✅ Saved hf data to {output_dir}hf.npy")
