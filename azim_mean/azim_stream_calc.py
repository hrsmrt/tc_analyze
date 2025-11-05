# python $WORK/tc_analyze/azim_mean/azim_stream_calc.py
# output: 流線関数
# 参考: Smith and Montgomery (2023) 5.61式
# はじめr = 0でz方向に積分し、その後はr方向に積分

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
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

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

r_max = 1000e3

nr = int(r_max / dx)
R = (np.arange(nr) + 0.5) * dx
f = 3.77468e-5

nz = 74

output_folder = "./data/azim/stream/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    rho = np.load(f"./data/azim/ms_rho/t{str(t).zfill(3)}.npy")
    u = np.load(f"./data/azim/wind_relative_radial/t{str(t).zfill(3)}.npy")
    w = np.load(f"./data/azim/ms_w/t{str(t).zfill(3)}.npy")
    phi = np.zeros_like(rho)
    for z in range(1,nz):
        phi[z,0] = phi[z-1,0] - 0.5 * (rho[z,0]*u[z,0]*R[0] + rho[z-1,0]*u[z-1,0]*R[0]) * (vgrid[z] - vgrid[z-1])
    for z in range(nz):
        for r in range(1,nr):
            phi[z,r] = phi[z,r-1] + 0.5 * (rho[z,r]*w[z,r]*R[r] + rho[z,r-1]*w[z,r-1]*R[r-1]) * (R[r] - R[r-1])

    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", phi)
    print(f"t={t} done")

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
