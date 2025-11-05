# python $WORK/tc_analyze/azim_mean/eliassen/azim_N2_calc.py
# input: f"./data/azim/buoyancy/t{str(t).zfill(3)}.npy" 温度
# output: N^2 = dB/dz

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

nz = 74
vgrid = np.loadtxt(f"{os.path.dirname(os.path.abspath(__file__))}/../../database/vgrid/vgrid_c74.txt")

time_list = [t * dt_hour for t in range(nt)]

r_max = 1000e3

nr = int(r_max / dx)
R = (np.arange(nr) + 0.5) * dx
f = 3.77468e-5

output_folder = "./data/azim/eliassen/N2/"
os.makedirs(output_folder, exist_ok=True)

pres_s = 100000  # 基準気圧 Pa
Rd = 287.05  # 気体定数 J/(kg·K)
Cp = 1005  # 定圧比熱 J/(kg·K)
L = 2.5e6  # 蒸発潜熱 J/kg

theta_ref = 300.0  # 基準温位 K

g = 9.80665

def process_t(t):
    b = np.load(f"./data/azim/eliassen/buoyancy/t{str(t).zfill(3)}.npy")
    db_dz = np.zeros((nz-1, nr))
    for z in range(nz-1):
        db_dz[z,:] = (b[z+1,:] - b[z,:]) / (vgrid[z+1] - vgrid[z])
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", db_dz)
    print(f"t={t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
