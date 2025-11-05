# python $WORK/tc_analyze/sums/sums_calc.py varname
import os
import sys
import numpy as np
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
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

extent = 500e3
extent_x = int(extent / dx)
extent_y = int(extent / dy)

z_max = 60

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

os.makedirs(str(f"./data/sums/"),exist_ok=True)

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)
X_cut = X[: extent_y * 2, : extent_x * 2]
Y_cut = Y[: extent_y * 2, : extent_x * 2]


vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

data_all = np.memmap(f"{input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(nt,nz,ny,nx))


def process_t(t):
    center_x = int(center_x_list[t]/dx)
    center_y = int(center_y_list[t]/dy)
    x_idx = [(center_x - extent_x + i) % nx for i in range(2 * extent_x)]
    y_idx = [(center_y - extent_y + i) % ny for i in range(2 * extent_y)]
    data = data_all[t,:z_max,:,:]
    data_cut = data[:, y_idx, :][:, :, x_idx]
    data_sum = data_cut.sum()
    return data_sum

sum_results = Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))

np.save(f"./data/sums/{varname}_sum.npy", sum_results)
