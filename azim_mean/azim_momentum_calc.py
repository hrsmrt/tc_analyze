# python $WORK/tc_analyze/azim_mean/azim_momentum_calc.py
# input: f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy"
# output: 単位質量あたりの角運動量 M = rv + f r^2/2

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

output_folder = "./data/azim/momentum/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    u_tangential = np.load(f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy")
    M = R * u_tangential + 0.5 * f * R**2
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", M)
    print(f"t={t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
