# python $WORK/tc_analyze/azim_mean/eliassen/azim_gamma_calc.py
# gamma = (v^2/r + fv)/g

import os
import numpy as np
import json
from joblib import Parallel, delayed

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
triangle_size = setting['triangle_size']
nx = 2 ** glevel
x_width = triangle_size
dx = x_width / nx

time_list = [t * dt_hour for t in range(nt)]

r_max = 1000e3

nr = int(r_max / dx)
R = (np.arange(nr) + 0.5) * dx
f = 3.77468e-5

output_folder = "./data/azim/eliassen/gamma/"
os.makedirs(output_folder, exist_ok=True)

pres_s = 100000  # 基準気圧 Pa
Rd = 287.05  # 気体定数 J/(kg·K)
Cp = 1005  # 定圧比熱 J/(kg·K)
L = 2.5e6  # 蒸発潜熱 J/kg



g = 9.80665

def process_t(t):
    v = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")
    gamma = (v[:,:]**2 / R[:] + f * v[:,:]) / g
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", gamma)
    print(f"t={t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
