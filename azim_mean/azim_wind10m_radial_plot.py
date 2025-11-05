# python $WORK/tc_analyze/azim_mean/azim_wind10m_radial_plot.py $style
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

folder = f"./fig/azim/wind10m_radial/"

os.makedirs(folder,exist_ok=True)

# メインループ
def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim/wind10m_radial/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,4))
    ax.plot(data)
    ax.set_xlabel("半径 [km]")

    fig.savefig(f"{folder}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
