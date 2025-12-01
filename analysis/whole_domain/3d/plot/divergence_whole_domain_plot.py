"""
Plot 3D divergence field over whole domain.

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約
"""
# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/divergence_whole_domain_plot.py $style

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)
F = config.f

OUTPUT_DIR = config.get_domain_path("whole_domain", "3d/divergence", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

# ✅ オンデマンド計算: メモリマップを開く
data_all_u = np.memmap(
    os.path.join(config.input_folder, "ms_u.grd"),
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_all_v = np.memmap(
    os.path.join(config.input_folder, "ms_v.grd"),
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def calculate_divergence(data_u, data_v, dx, dy):
    """
    Calculate divergence of horizontal wind field.

    Parameters
    ----------
    data_u : np.ndarray
        U-component of wind (nz, ny, nx)
    data_v : np.ndarray
        V-component of wind (nz, ny, nx)
    dx : float
        Grid spacing in x-direction
    dy : float
        Grid spacing in y-direction

    Returns
    -------
    div : np.ndarray
        Divergence field (nz, ny, nx)
    """
    # ベクトル化版: 全Z方向を一度に処理
    du_dx = (np.roll(data_u, -1, axis=2) - np.roll(data_u, 1, axis=2)) / (2 * dx)
    dv_dy = (np.roll(data_v, -1, axis=1) - np.roll(data_v, 1, axis=1)) / (2 * dy)

    # 境界条件の処理（北極と南極）
    nx = data_u.shape[2]
    dv_dy[:, 0, : nx // 2] = (data_v[:, 1, : nx // 2] - data_v[:, -1, nx // 2:]) / (2 * dy)
    dv_dy[:, 0, nx // 2:] = (data_v[:, 1, nx // 2:] - data_v[:, -1, : nx // 2]) / (2 * dy)
    dv_dy[:, -1, : nx // 2] = (data_v[:, 0, : nx // 2] - data_v[:, -2, nx // 2:]) / (2 * dy)
    dv_dy[:, -1, nx // 2:] = (data_v[:, 0, nx // 2:] - data_v[:, -2, : nx // 2]) / (2 * dy)

    return du_dx + dv_dy


def process_t(t):
    """
    Process a single time step to create divergence plots.

    Parameters
    ----------
    t : int
        Time step index
    """
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    data_u = data_all_u[t]  # shape: (nz, ny, nx)
    data_v = data_all_v[t]  # shape: (nz, ny, nx)

    # 発散を計算
    data_z = calculate_divergence(data_u, data_v, config.dx, config.dy)

    X_km, Y_km = grid.get_meshgrid_km()
    for z in z_list:
        data = data_z[z]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 4))
        c = ax.contourf(
            X_km,
            Y_km,
            data,
            cmap="bwr",
            levels=np.arange(-0.002, 0.0022, 0.0002),
            extend="both",
        )
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(
            "right", size="5%", pad=0.1
        )  # size: colorbar幅, pad: 図との距離
        cbar = fig.colorbar(c, cax=cax)
        cbar.set_ticks([-0.002, 0.002])
        ax.set_title(f"t={config.time_list[t]:3d}h,z={int(vgrid[z] * 1e-2) * 1e-1}km")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        fig.savefig(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
