# python $WORK/tc_analyze/azim_mean/azim_wind_relative_tangential_max_z_plot.py $style
# 各高度での最大値をプロット
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

# グリッド設定
vgrid = grid.create_vertical_grid()

output_folder = "./fig/azim/wind_relative_tangential_max_z/"

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    data = np.load(f"./data/azim/wind_relative_tangential/t{str(t).zfill(3)}.npy")
    max_z_data = np.nanmax(data, axis=1)  # 各高度での最大値を計算

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    ax.plot(max_z_data, vgrid)
    ax.set_title(f"方位角平均最大接線風 t = {config.time_list[t]} hour")
    ax.set_xlim([0, 80e3])
    ax.set_ylim([0, 20e3])
    ax.set_yticks([0, 5e3, 10e3, 15e3, 20e3], ["", "", "", "", ""])
    ax.set_xlabel("風速 [m/s]")
    ax.set_ylabel("高度 [km]")
    # plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(config.dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
    plt.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
