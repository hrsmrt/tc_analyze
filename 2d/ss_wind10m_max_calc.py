# python $WORK/tc_analyze/analyze/2d/ss_wind10m_max_calc.py
import numpy as np
import json
import os

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
nx = 2 ** glevel
ny = 2 ** glevel

input_folder = setting["input_folder"]

output_folder = "./data/"
os.makedirs(output_folder, exist_ok=True)

ss_u10m = np.fromfile(f"{input_folder}ss_u10m.grd",dtype=">f4").reshape(nt,ny,nx)
ss_v10m = np.fromfile(f"{input_folder}ss_v10m.grd",dtype=">f4").reshape(nt,ny,nx)

data_abs = np.sqrt(ss_v10m**2 + ss_u10m**2)
data_abs_max = data_abs.max(axis=(1, 2))

np.save(f"{output_folder}ss_wind10m_max.npy", data_abs_max)
