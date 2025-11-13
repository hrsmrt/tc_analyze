# python $WORK/tc_analyze/azim_mean/azim_plot_momentum_theta_e.py $style

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

OUTPUT_FOLDER = "./fig/azim/momentum_theta_e/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_t(t):
    # 運動量データの読み込み
    momentum_data = np.load(f"./data/azim/momentum/t{str(t).zfill(3)}.npy")

    # グリッド設定：データから実際のビン数を取得
    nr = momentum_data.shape[1]
    R_MAX = nr * config.dx
    r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

    # km単位に変換
    r_mesh_km = r_mesh * 1e-3
    z_mesh_km = z_mesh * 1e-3

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))

    # 運動量データのプロット
    contour_filled = ax.contourf(
        r_mesh_km,
        z_mesh_km,
        momentum_data,
        extend="max",
        levels=np.arange(0, 2.8e7, 2e6),
    )
    fig.colorbar(contour_filled, ax=ax)

    # 相当温位データの読み込みと等値線プロット
    theta_e_data = np.load(f"./data/azim/theta_e/t{str(t).zfill(3)}.npy")

    # theta_eのデータサイズが異なる場合は、theta_e用のグリッドを生成
    if theta_e_data.shape[1] != nr:
        nr_theta = theta_e_data.shape[1]
        R_MAX_theta = nr_theta * config.dx
        r_mesh_theta, z_mesh_theta = grid.create_radial_vertical_meshgrid(R_MAX_theta)
        r_mesh_km_theta = r_mesh_theta * 1e-3
        z_mesh_km_theta = z_mesh_theta * 1e-3
    else:
        r_mesh_km_theta = r_mesh_km
        z_mesh_km_theta = z_mesh_km

    ax.contour(
        r_mesh_km_theta,
        z_mesh_km_theta,
        theta_e_data,
        levels=np.arange(330, 375, 5),
        colors="black",
        linewidths=0.5,
    )

    ax.set_ylim([0, 20])
    ax.set_title(f"t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(f"{OUTPUT_FOLDER}t{str(t).zfill(3)}.png")
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
