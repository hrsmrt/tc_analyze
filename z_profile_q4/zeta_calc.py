# python $WORK/tc_analyze/z_profile_q4/zeta_calc.py

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

output_dir = f"./data/z_profile_q4/zeta/"
os.makedirs(output_dir,exist_ok=True)

for q in ["q0","q1","q2","q3"]:
    os.makedirs(f"{output_dir}{q}/",exist_ok=True)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

x  = np.arange(0,x_width,dx) + dx/2
y  = np.arange(0,y_width,dy) + dy/2
X,Y = np.meshgrid(x,y)

R_max = 300e3

# --- 出力配列 (nt, nz, 4象限) ---
z_profile_q = np.zeros((nt, nz, 4))

for t in range(nt):
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = X - cx
    dY = Y - cy
    # 周期境界補正
    dX[dX >  0.5*x_width] -= x_width
    dX[dX < -0.5*x_width] += x_width
    R = np.sqrt(dX**2 + dY**2)

    # --- マスク（半径R_max以内）---
    mask_R = (R <= R_max)

    # --- 方位角 θ (北を0°, 半時計回りに増加) ---
    theta = np.arctan2(dY, dX)
    theta = (theta + np.pi/2) % (2*np.pi)  # 北=0, 東=90°, 南=180°, 西=270°

    # --- 象限番号 (0: 北東, 1: 南東, 2: 南西, 3: 北西) ---
    # 例: 0〜π/2 → 北東, π/2〜π → 南東, π〜3π/2 → 南西, 3π/2〜2π → 北西
    sector = np.floor(theta / (np.pi/2)).astype(int)  # 0〜3

    for z in range(nz):
        filename = f"t{str(t+1).zfill(4)}z{str(z+1).zfill(2)}.dat"
        filepath = f"./data/zeta/{filename}"
        data = read_fortran_unformatted(filepath, np.float32).reshape(ny, nx)

        # 半径R_max内のみ
        data_masked = np.where(mask_R, data, np.nan)

        # 象限ごとの平均
        for q in range(4):
            q_mask = (sector == q)
            vals = data_masked[q_mask]
            if np.isfinite(vals).any():
                z_profile_q[t, z, q] = np.nanmean(vals)
            else:
                z_profile_q[t, z, q] = np.nan

    print(f"Processed time step {t+1}/{nt}")

# --- 保存 ---
os.makedirs(output_dir, exist_ok=True)
np.save(f"{output_dir}z_zeta_quadrants.npy", z_profile_q)
print(f"✅ Saved quadrant profiles for zeta to {output_dir}z_zeta_quadrants.npy")
