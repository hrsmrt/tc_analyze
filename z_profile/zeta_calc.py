# python $WORK/tc_analyze/z_profile/zeta_calc.py

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "module"))
sys.path.append(module_path)
from input_data import read_fortran_unformatted
import numpy as np
from joblib import Parallel, delayed

# ファイルを開いてJSONを読み込む
from utils.config import AnalysisConfig

config = AnalysisConfig()

# === 保存 ===
os.makedirs(output_dir, exist_ok=True)
np.save(f"{output_dir}z_zeta.npy", z_profile_all)
print(f"✅ Saved z_profile data for zeta to {output_dir}z_zeta.npy")
