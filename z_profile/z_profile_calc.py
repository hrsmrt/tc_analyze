# python $WORK/tc_analyze/z_profile/z_profile_calc.py

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, '../../module')
sys.path.append(target_path)
import numpy as np
import json
from joblib import Parallel, delayed

varname = sys.argv[1]

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
nx = 2 ** glevel
ny = 2 ** glevel
nz = 74
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

out_dir = f"./data/z_profile/"
os.makedirs(out_dir,exist_ok=True)

data_memmap = np.memmap(f"{input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(nt, nz, ny, nx))

z_profile_all = data_memmap.mean(axis=(2,3))

np.save(f"./data/z_profile/z_{varname}.npy", z_profile_all)
print(f"Saved z_profile data for {varname} to ./data/z_profile/z_{varname}.npy")
