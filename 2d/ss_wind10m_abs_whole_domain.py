# python $WORK/tc_analyze/analyze/2d/ss_wind10m_abs_whole_domain.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument
from joblib import Parallel, delayed

mpl_style_sheet = parse_style_argument(arg_index=1)

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:20] = [1, 1, 1, 1]  # 下限の20色を白に設定
custom_cmap = ListedColormap(colors)

output_dir = "./fig/2d/whole_domain/wind10m_abs/"
os.makedirs(output_dir,exist_ok=True)

# 設定の初期化
config = AnalysisConfig()
grid = GridHandler(config)
ss_u10m = np.fromfile(f"{config.input_folder}ss_u10m.grd",dtype=">f4").reshape(config.nt,config.ny,config.nx)
ss_v10m = np.fromfile(f"{config.input_folder}ss_v10m.grd",dtype=">f4").reshape(config.nt,config.ny,config.nx)
data_abs = np.sqrt(ss_v10m**2 + ss_u10m**2)

def process_t(t):
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2,2))
    c = ax.contourf(grid.X, grid.Y,data_abs[t],cmap=custom_cmap,levels=np.arange(0,51,5),extend='max')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    ax.set_xticks([0, config.x_width * 1/2, config.x_width],["","",""])
    ax.set_yticks([0, config.y_width * 1/2, config.y_width],["","",""])
    ax.set_title(f"10m風速 t = {config.time_list[t]} h")
    ax.set_aspect('equal', 'box')
    ax.grid(False)
    fig.savefig(f"{output_dir}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
