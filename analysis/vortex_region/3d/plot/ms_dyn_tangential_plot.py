"""
ms_dyn_tangential のプロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することでストレージを節約

プロット処理を実行します。
"""

# python $WORK/tc_analyze/analysis/vortex_region/3d/plot/ms_dyn_tangential_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_km
from utils.wind import calculate_absolute_wind_radial_tangential

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く（保存データ不要）
data_u = np.memmap(
    os.path.join(config.input_folder, "ms_u.grd"),
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_v = np.memmap(
    os.path.join(config.input_folder, "ms_v.grd"),
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)

OUTPUT_DIR = config.get_fig_path("3d", "vortex_region", "dyn_tangential")

os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    _, v_tangential = calculate_absolute_wind_radial_tangential(
        data_u, data_v, t, center_x_list, center_y_list, grid
    )
    data_t = v_tangential
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
            levels=np.arange(-30, 35, 5),
            extend="both",
        )
        fig.colorbar(c, ax=ax)
        set_vortex_region_ticks_km(ax, EXTENT)
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")
        fig.savefig(
            os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png")
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
