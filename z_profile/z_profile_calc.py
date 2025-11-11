# python $WORK/tc_analyze/z_profile/z_profile_calc.py

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, '../../module')
sys.path.append(target_path)
import numpy as np
from joblib import Parallel, delayed

varname = sys.argv[1]

from utils.config import AnalysisConfig

config = AnalysisConfig()

time_list = [t * config.dt_hour for t in range(config.nt)]

out_dir = f"./data/z_profile/"
os.makedirs(out_dir,exist_ok=True)

data_memmap = np.memmap(f"{config.input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(config.nt, config.nz, config.ny, config.nx))

z_profile_all = data_memmap.mean(axis=(2,3))

np.save(f"./data/z_profile/z_{varname}.npy", z_profile_all)
print(f"Saved z_profile data for {varname} to ./data/z_profile/z_{varname}.npy")
