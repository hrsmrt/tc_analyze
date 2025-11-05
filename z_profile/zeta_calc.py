# python $WORK/tc_analyze/z_profile/zeta_calc.py

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "module"))
sys.path.append(module_path)
from input_data import read_fortran_unformatted
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
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

output_dir = f"./data/z_profile/zeta/"
os.makedirs(output_dir,exist_ok=True)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

x  = np.arange(0,x_width,dx) + dx/2
y  = np.arange(0,y_width,dy) + dy/2
X,Y = np.meshgrid(x,y)

R_max = 300e3

z_profile_all = np.zeros((nt, nz))

for t in range(nt):
    cx = center_x_list[t]
    cy = center_y_list[t]
    dX = X - cx
    dY = Y - cy
    dX[dX >  0.5*x_width] -= x_width
    dX[dX < -0.5*x_width] += x_width
    R = np.sqrt(dX**2 + dY**2)
    iy, ix = np.where(R <= R_max)

    for z in range(nz):
        filename = f"t{str(t+1).zfill(4)}z{str(z+1).zfill(2)}.dat"
        filepath = f"./data/zeta/{filename}"
        data = read_fortran_unformatted(filepath, np.float32)
        data = data.reshape(ny,nx)
        z_profile_all[t,z] = np.mean(data[iy,ix])
    print(f"Processed time step {t+1}/{nt}")


# === 保存 ===
os.makedirs(output_dir, exist_ok=True)
np.save(f"{output_dir}z_zeta.npy", z_profile_all)
print(f"✅ Saved z_profile data for zeta to {output_dir}z_zeta.npy")
