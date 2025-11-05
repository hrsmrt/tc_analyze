# python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_max_plot.py $style
import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
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
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

folder = f"./fig/azim/wind10m_tangential/"

os.makedirs(folder,exist_ok=True)

wind10m_tangential_max = np.load(f"./data/azim/wind10m_tangential/wind10m_tangential_max.npy")
wind10m_tangential_rmw = np.load(f"./data/azim/wind10m_tangential/wind10m_tangential_rmw.npy")


fig, ax = plt.subplots(figsize=(5,4))
ax.plot(time_list[1:], wind10m_tangential_max[1:])
ax.set_xlabel("時間 [h]")
ax.set_ylabel("方位角平均最大風速 [m/s]")
fig.savefig(f"{folder}max.png")
plt.close()

fig, ax = plt.subplots(figsize=(5,4))
ax.plot(time_list[1:], wind10m_tangential_rmw[1:]*1e-3)
ax.set_ylim(0, None)
ax.set_xlabel("時間 [h]")
ax.set_ylabel("方位角平均最大風速半径 [km]")
fig.savefig(f"{folder}rmw.png")
plt.close()
