# python $WORK/tc_analyze/z_profile/hf_calc.py
# hf: moist static energy, Nolan+2007 (3)式

import os
import sys
import numpy as np
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "..", "module"))
sys.path.append(module_path)
from joblib import Parallel, delayed

cp = 1004 # J/kg/K
L = 2.5e6 # J/kg, An introduction to clouds, Table 2.1(温度依存性あり)
Lv = 2.8e6 # J/kg, An introduction to clouds, Table 2.1(温度依存性あり)
g = 9.81 # m/s

# ファイルを開いてJSONを読み込む
from utils.config import AnalysisConfig

config = AnalysisConfig()

def hf_t(t):
    T  = files["tem"][t].mean(axis=(1,2))
    qv = files["qv"][t].mean(axis=(1,2))
    qg = files["qg"][t].mean(axis=(1,2))

    hf = cp * T + g * vgrid + L * qv + Lv * qg
    return hf

hf_all = Parallel(n_jobs=n_jobs)(delayed(hf_t)(t) for t in range(config.nt))

hf_all = np.array(hf_all)
np.save(f"{out_dir}hf.npy", hf_all)
