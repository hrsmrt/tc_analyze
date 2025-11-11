# python $WORK/tc_analyze/z_profile_q4/zeta_plot.py $style

import os
import sys
# 実行ファイル（この.pyファイル）を基準に相対パスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
target_path = os.path.join(script_dir, '../../module')
sys.path.append(target_path)
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

time_list = [t * config.dt_hour for t in range(config.nt)]

vgrid = np.loadtxt(f"{setting['vgrid_filepath']}")

X, Y = np.meshgrid(time_list, vgrid)

output_dir = f"./fig/z_profile_q4/zeta/"
os.makedirs(output_dir,exist_ok=True)
for q in range(4):
    os.makedirs(f"{output_dir}q{q}/",exist_ok=True)

data_all = np.load(f"./data/z_profile_q4/zeta/z_zeta_quadrants.npy")

for q in range(4):
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(7,2.5))
    ax.set_xlim(0,time_list[-1])
    ax.set_ylim(0,20e3)
    ax.set_xticks([0,24,48,72,96,120,144,168,192,216,240])
    ax.set_title(f"渦度")
    ax.set_ylabel('高度 [km]')
    ax.set_xlabel('時間 [hour]')
    c = ax.contourf(X,Y,data_all[:,:,q].T,levels=np.arange(0,0.00022,0.00002),cmap="rainbow",extend="max")
    fig.colorbar(c, ax=ax)
    fig.savefig(os.path.join(output_dir, f'all_q{q}.png'))
    plt.close()

for q in range(4):
    for t in range(config.nt):
        data = data_all[t, :, q]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(data,vgrid)
        ax.set_xlim(-0.00005,0.00025)
        ax.set_ylim(0,20e3)
        ax.set_ylabel('高度 [km]')
        ax.set_xlabel('')
        ax.set_title(f't = {time_list[t]} hour')
        fig.savefig(f"{output_dir}q{q}/t{time_list[t]:04d}h.png")
        plt.close()
        print(f"q{q} t{t} done")
