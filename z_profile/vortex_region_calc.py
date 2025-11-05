# python $WORK/tc_analyze/z_profile/vortex_region_calc.py varname

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

output_dir = f"./data/z_profile/vortex_region/"
os.makedirs(output_dir,exist_ok=True)

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

x  = np.arange(0,x_width,dx) + dx/2
y  = np.arange(0,y_width,dy) + dy/2
X,Y = np.meshgrid(x,y)

R_max = 500e3

# === 入力 ===
data_memmap = np.memmap(
    f"{input_folder}{varname}.grd",
    dtype=">f4", mode="r",
    shape=(nt, nz, ny, nx)
)

z_profile_all = np.zeros((nt, nz))

# === 並列処理関数 ===
def process_t(t):
    cx = center_x_list[t]
    cy = center_y_list[t]
    dX = X - cx
    dY = Y - cy
    dX[dX >  0.5*x_width] -= x_width
    dX[dX < -0.5*x_width] += x_width
    R = np.sqrt(dX**2 + dY**2)
    iy, ix = np.where(R <= R_max)

    data = data_memmap[t]
    profile = np.mean(data[:, iy, ix], axis=1, dtype=np.float64)

    print(f"t={t:03d}: mean={profile.mean():.3e}")
    return profile


# === 並列実行 ===
results = Parallel(n_jobs=8, verbose=5)(delayed(process_t)(t) for t in range(nt))

# === 結果をまとめる ===
z_profile_all = np.stack(results, axis=0)

# === 保存 ===
os.makedirs(output_dir, exist_ok=True)
np.save(f"{output_dir}z_{varname}.npy", z_profile_all)
print(f"✅ Saved z_profile data for {varname} to {output_dir}z_{varname}.npy")
