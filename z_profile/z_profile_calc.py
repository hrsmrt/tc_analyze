# python $WORK/tc_analyze/z_profile/z_profile_calc.py

import os
import sys
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

varname = sys.argv[1]

# 出力ディレクトリ
output_dir = "./data/z_profile/"
os.makedirs(output_dir, exist_ok=True)

# データの読み込みと処理
data_memmap = np.memmap(
    f"{config.input_folder}{varname}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx)
)

z_profile_all = data_memmap.mean(axis=(2, 3))

# 保存
np.save(f"{output_dir}z_{varname}.npy", z_profile_all)
print(f"✅ Saved z_profile data for {varname} to {output_dir}z_{varname}.npy")
