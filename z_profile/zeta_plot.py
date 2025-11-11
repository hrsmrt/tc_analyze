# python $WORK/tc_analyze/z_profile/zeta_plot.py $style

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

# ファイルを開いてJSONを読み込む
from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

def process_t(t):
    data = data_all[t, :]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(data,vgrid)
    ax.set_xlim(-0.00005,0.00025)
    ax.set_ylim(0,20e3)
    ax.set_ylabel('高度 [km]')
    ax.set_xlabel('')
    ax.set_title(f't = {time_list[t]} hour')
    fig.savefig(os.path.join(out_dir, f't{time_list[t]:04d}h.png'))
    plt.close()

Parallel(n_jobs=n_jobs)(delayed(process_t)(t) for t in range(config.nt))
