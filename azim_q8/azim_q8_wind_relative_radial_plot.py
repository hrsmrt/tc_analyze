# python $WORK/tc_analyze/azim_q8/azim_q8_wind_relative_radial_plot.py $style
import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import matplotlib.pyplot as plt
import json
from joblib import Parallel, delayed
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
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
n_jobs = setting.get("n_jobs", 1)

time_list = [t * dt_hour for t in range(nt)]

vgrid = np.loadtxt(f"{setting['vgrid_filepath']}")

nr = 1000e3/dx
xgrid = np.arange(nr) * dx

X, Y = np.meshgrid(xgrid,vgrid)

folder = f"./fig/azim_q8/wind_relative_radial/"

os.makedirs(folder,exist_ok=True)

sector_names = [f"sector{s}" for s in range(8)]


def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim_q8/wind_relative_radial/t{str(t).zfill(3)}.npy")

    # 各sectorごとにプロット
    for s in range(8):
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5,2))
        data_s = data[:,:,s]
        if t < 96:
            c = ax.contourf(X,Y,data_s,cmap="bwr",levels=np.arange(-30,35,5),extend="both")
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-30,0,30])
        else:
            c = ax.contourf(X,Y,data_s,cmap="bwr",levels=np.arange(-60,70,10),extend="both")
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-60,0,60])
        ax.set_ylim([0, 20e3])
        ax.set_title(f"{sector_names[s]} 動径風速 t = {time_list[t]} hour")
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("高度 [km]")

        sec_folder = os.path.join(folder, sector_names[s])
        os.makedirs(sec_folder, exist_ok=True)
        fig.savefig(f"{sec_folder}/t{str(t).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=n_jobs)(delayed(process_t)(t) for t in range(nt))
