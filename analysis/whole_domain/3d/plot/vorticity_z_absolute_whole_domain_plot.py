"""
Plot 3D absolute vorticity field over whole domain.

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約
"""
# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/vorticity_z_absolute_whole_domain_plot.py $style
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
from utils.vorticity import calculate_vorticity_z

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)
F = config.f

OUTPUT_DIR = config.get_domain_path("whole_domain", "3d/vorticity_z_absolute", data_type="fig")
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


def process_t(t):
    """
    Process a single time step to create absolute vorticity plots.

    Parameters
    ----------
    t : int
        Time step index
    """
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    data_u = data_all_u[t]  # shape: (nz, ny, nx)
    data_v = data_all_v[t]  # shape: (nz, ny, nx)

    # 渦度を計算 (utils/vorticity.py の共通関数を使用)
    data_z = calculate_vorticity_z(data_u, data_v, config.dx, config.dy)

    X_km, Y_km = grid.get_meshgrid_km()
    for z in z_list:
        data = data_z[z]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 4))
        c = ax.contourf(X_km, Y_km, data + F, cmap="rainbow")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(
            "right", size="5%", pad=0.1
        )  # size: colorbar幅, pad: 図との距離
        fig.colorbar(c, cax=cax)
        ax.set_title(f"t={config.time_list[t]:3d}h,z={int(vgrid[z] * 1e-2) * 1e-1}km")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        fig.savefig(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
