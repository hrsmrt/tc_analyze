# python $WORK/tc_analyze/analyze/2d/ss_wind10m_radial_plot.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_km_empty
from joblib import Parallel, delayed

mpl_style_sheet = parse_style_argument()

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:40] = [1, 1, 1, 1]  # 0に相当する位置（真ん中）を白に変更
custom_cmap = ListedColormap(colors)

folder_input = "./data/2d/wind10m_radial/"
output_dir = "./fig/2d/vortex_region/wind10m_radial/"
os.makedirs(output_dir,exist_ok=True)

# 設定の初期化
config = AnalysisConfig()
grid = GridHandler(config)
extent = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

# GridHandlerから切り出し領域のメッシュグリッドを取得
X_cut, Y_cut = grid.get_vortex_region_meshgrid(extent)

def process_t(t):
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    data = np.load(f"{folder_input}t{str(t).zfill(3)}.npy")
    data_cut = grid.extract_vortex_region(data, center_x, center_y, extent)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5,2.5))
    c = ax.contourf(X_cut*1e-3,Y_cut*1e-3,data_cut,cmap=custom_cmap,levels=np.arange(0,5.5,0.5),extend='max')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    set_vortex_region_ticks_km_empty(ax, extent)
    # ax.set_xticks([0, extent_x * config.dx * 1e-3, 2 * extent_x * config.dx * 1e-3],[-int(extent_x * config.dx * 1e-3),0, int(extent_x * config.dx * 1e-3)])
    # ax.set_yticks([0, extent_y * config.dy * 1e-3, 2 * extent_y * config.dy * 1e-3],[-int(extent_y * config.dy * 1e-3),0, int(extent_y * config.dy * 1e-3)])
    # ax.set_xlabel("x [km]")
    # ax.set_ylabel("y [km]")

    ax.set_aspect('equal', 'box')
    plt.savefig(f"{output_dir}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
