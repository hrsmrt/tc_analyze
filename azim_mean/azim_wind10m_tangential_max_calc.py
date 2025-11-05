# python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_max_calc.py
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
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

folder = f"./data/azim/wind10m_tangential/"

os.makedirs(folder,exist_ok=True)

# メインループ
def process_t(t):
    # データの読み込み
    data = np.load(f"{folder}t{str(t).zfill(3)}.npy")
    return data.max(), data.argmax()*dx

max_values = Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))

max_values = np.array(max_values)

wind10m_tangential_max = max_values[:, 0]
wind10m_tangential_rmw = max_values[:, 1]


np.save(f"{folder}wind10m_tangential_max.npy", wind10m_tangential_max)
np.save(f"{folder}wind10m_tangential_rmw.npy", wind10m_tangential_rmw)

