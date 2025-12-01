"""
divergence_vortex_region のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/analysis/vortex_region/3d/plot/divergence_vortex_region_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

OUTPUT_DIR = config.get_tc_centric_path("vortex_region", "3d/divergence", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")


def process_t(t):
    # npz/npy fallback
    data_dir = config.get_domain_path("whole_domain", "3d/divergence")
    npz_path = os.path.join(data_dir, f"div_t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_dir, f"div_t{str(t).zfill(3)}.npy")
    if os.path.exists(npz_path):
        with np.load(npz_path) as npz_file:
            data_t = npz_file["data"]
    else:
        data_t = np.load(npy_path)
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data = data_t[z, :, :]
        data_cut = grid.extract_vortex_region(data, center_x, center_y, EXTENT)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        c = ax.contourf(
            X_cut,
            Y_cut,
            data_cut,
            cmap="bwr",
            levels=np.arange(-0.002, 0.0022, 0.0002),
            extend="both",
        )
        cbar = fig.colorbar(c, ax=ax)
        cbar.set_ticks([-0.002, 0.002])
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal", "box")
        fig.savefig(
            os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}", f"t{str(config.time_list[t]).zfill(3)}.png")
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
