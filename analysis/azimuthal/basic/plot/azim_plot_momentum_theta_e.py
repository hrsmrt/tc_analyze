# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_plot_momentum_theta_e.py $style

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

OUTPUT_FOLDER = config.get_tc_centric_path("azimuthal", "basic/momentum_theta_e", data_type="fig")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def process_t(t):
    # 運動量データの読み込み（.npz優先、.npyフォールバック）
    momentum_path = config.get_tc_centric_path("azimuthal", "basic/momentum")
    momentum_npz = os.path.join(momentum_path, f"t{str(t).zfill(3)}.npz")
    momentum_npy = os.path.join(momentum_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(momentum_npz):
        npz_data = np.load(momentum_npz)
        momentum_data = npz_data['data']
    elif os.path.exists(momentum_npy):
        momentum_data = np.load(momentum_npy)
    else:
        raise FileNotFoundError(f"Neither {momentum_npz} nor {momentum_npy} found")

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

    # 相当温位データの読み込みと等値線プロット（.npz優先、.npyフォールバック）
    theta_e_path = config.get_tc_centric_path("azimuthal", "basic/theta_e")
    theta_e_npz = os.path.join(theta_e_path, f"t{str(t).zfill(3)}.npz")
    theta_e_npy = os.path.join(theta_e_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(theta_e_npz):
        npz_data = np.load(theta_e_npz)
        theta_e_data = npz_data['data']
    elif os.path.exists(theta_e_npy):
        theta_e_data = np.load(theta_e_npy)
    else:
        raise FileNotFoundError(f"Neither {theta_e_npz} nor {theta_e_npy} found")

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
    fig.savefig(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.png"))
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
