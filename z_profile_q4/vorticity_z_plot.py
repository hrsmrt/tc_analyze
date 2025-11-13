# python $WORK/tc_analyze/z_profile_q4/vorticity_z_plot.py $style

import os

import matplotlib.pyplot as plt
import numpy as np

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

# 時刻範囲のリストを作成
time_list = [config.time_list[t] for t in range(config.t_first, config.t_last)]

# 鉛直グリッドを取得 (km単位)
vgrid = grid.create_vertical_grid() * 1e-3

X, Y = np.meshgrid(time_list, vgrid)

output_dir = "./fig/z_profile_q4/zeta/"
os.makedirs(output_dir, exist_ok=True)
for q in range(4):
    os.makedirs(f"{output_dir}q{q}/", exist_ok=True)

data_all = np.load("./data/z_profile_q4/zeta/z_zeta_quadrants.npy")

for q in range(4):
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.set_xlim(0, time_list[-1])
    ax.set_ylim(0, 20)
    ax.set_xticks([0, 24, 48, 72, 96, 120, 144, 168, 192, 216, 240])
    ax.set_title("渦度")
    ax.set_ylabel("高度 [km]")
    ax.set_xlabel("時間 [hour]")
    c = ax.contourf(
        X,
        Y,
        data_all[config.t_first : config.t_last, :, q].T,
        levels=np.arange(0, 0.00022, 0.00002),
        cmap="rainbow",
        extend="max",
    )
    fig.colorbar(c, ax=ax)
    fig.savefig(os.path.join(output_dir, f"all_q{q}.png"))
    plt.close()

for q in range(4):
    for i, t in enumerate(range(config.t_first, config.t_last)):
        data = data_all[t, :, q]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(data, vgrid)
        ax.set_xlim(-0.00005, 0.00025)
        ax.set_ylim(0, 20)
        ax.set_ylabel("高度 [km]")
        ax.set_xlabel("")
        ax.set_title(f"t = {time_list[i]} hour")
        fig.savefig(f"{output_dir}q{q}/t{int(time_list[i]):04d}h.png")
        plt.close()
        print(f"q{q} t={t} done")
