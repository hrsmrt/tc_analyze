# python $WORK/tc_analyze/azim_mean/azim_theta_e_calc.py
# input: f"./data/azim/ms_tem/t{str(t).zfill(3)}.npy" 温度
# input: f"./data/azim/ms_pres/t{str(t).zfill(3)}.npy" 気圧
# input: f"./data/azim/ms_qv/t{str(t).zfill(3)}.npy" 比湿
# output: 相当温位 θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))

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

output_folder = "./data/azim/theta_e/"
os.makedirs(output_folder, exist_ok=True)

pres_s = 100000  # 基準気圧 Pa
Rd = 287.05  # 気体定数 J/(kg·K)
Cp = 1005  # 定圧比熱 J/(kg·K)
L = 2.5e6  # 蒸発潜熱 J/kg

def process_t(t):
    tem = np.load(f"./data/azim/ms_tem/t{str(t).zfill(3)}.npy")
    pres = np.load(f"./data/azim/ms_pres/t{str(t).zfill(3)}.npy")
    qv = np.load(f"./data/azim/ms_qv/t{str(t).zfill(3)}.npy")
    rv = qv / (1 - qv)
    theta_e = tem * (pres_s / pres) ** (Rd / Cp) * np.exp(L * rv / (Cp * tem))
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", theta_e)
    print(f"t={t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
