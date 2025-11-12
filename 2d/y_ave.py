# python $WORK/tc_analyze/analyze/2d/y_ave.py varname $style
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import sys

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

#from joblib import Parallel, delayed
varname = sys.argv[1]
mpl_style_sheet = parse_style_argument()

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:3] = [1, 1, 1, 1]  # 0に相当する位置（真ん中）を白に変更
custom_rainbow = ListedColormap(colors)

# 設定の初期化
config = AnalysisConfig()
dir = f"./fig/2d/y_ave/{varname}/"
os.makedirs(dir, exist_ok=True)

y = np.arange(0, config.y_width, config.dy)

data_all = np.memmap(
    f"{config.input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(config.nt, config.ny, config.nx)
)

for t in range(config.t_first, config.t_last):
    data = data_all[t].mean(axis=1)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5,2))
    title = f"t = {config.time_list[t]}h"
    c = ax.plot(y,data)
    ax.set_title(title)
    ax.set_yticks([0, config.y_width * 0.25, config.y_width * 0.5, config.y_width * 0.75, config.y_width],["","","","",""])
    # ax.set_xlabel("x [km]")
    # ax.set_ylabel("y [km]")
    fig.savefig(f"{dir}t{str(config.time_list[t]).zfill(4)}.png")
    plt.close()

#Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
