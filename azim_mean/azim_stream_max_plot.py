# python $WORK/tc_analyze/azim_mean/azim_stream_max_plot.py $style

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
from joblib import Parallel, delayed

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    plt.style.use(mpl_style_sheet)
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

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

vgrid = np.loadtxt(f"{os.path.dirname(os.path.abspath(__file__))}/../../database/vgrid/vgrid_c74.txt")

time_list = [t * dt_hour for t in range(nt)]

r_max = 1000e3

nr = int(r_max / dx)
R = (np.arange(nr) + 0.5) * dx
f = 3.77468e-5

X, Y = np.meshgrid(R, vgrid)

input_folder = "./data/azim/stream/"
output_folder = "./fig/azim/stream/"
os.makedirs(output_folder, exist_ok=True)

max_phi = []
for t in range(nt):
    data = np.load(f"{input_folder}t{str(t).zfill(3)}.npy")
    print(f"t={t} max: {np.nanmax(data)}")
    max_phi.append(np.nanmax(data))

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5,2))
plt.plot(time_list, max_phi)
ax.set_title(f"流線関数の最大値")
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最大値")
fig.savefig(f"{output_folder}max.png")
plt.close()
