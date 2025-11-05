# python $WORK/tc_analyze/2d/ss_slp_min_calc.py
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

data = np.fromfile(f"{input_folder}ss_slp.grd", dtype=">f4").reshape(nt, ny, nx)
data_min = data.min(axis=(1, 2))
np.save(f"{output_folder}ss_slp_min.npy", data_min)
