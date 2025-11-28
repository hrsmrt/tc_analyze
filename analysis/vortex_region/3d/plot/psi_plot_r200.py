"""
psi_r200 のプロット

✅ ストレージ節約版: 完全オンデマンド計算を使用
u/vから渦度を計算し、さらに流線関数を計算
データ保存不要で数GB〜数百GBのストレージを節約

プロット処理を実行します。
"""

# python $WORK/tc_analyze/analysis/vortex_region/3d/plot/psi_plot_r200.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_empty
from utils.streamfunction import calculate_streamfunction
from utils.vorticity import calculate_vorticity_z

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 200e3

center_x_list = config.center_x
center_y_list = config.center_y

OUTPUT_FOLDER = config.get_tc_centric_path("vortex_region", "3d/psi_r200", data_type="fig")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_FOLDER, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

# u/vデータの読み込み（memmap使用）
u_all = np.memmap(
    f"{config.input_folder}ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
v_all = np.memmap(
    f"{config.input_folder}ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ 完全オンデマンド計算: u/vから渦度を計算し、さらに流線関数を計算（保存データ不要）
    u_t = u_all[t, :, :, :]
    v_t = v_all[t, :, :, :]
    vorticity_z = calculate_vorticity_z(u_t, v_t, config.dx, config.dy)
    data_t = calculate_streamfunction(vorticity_z, config.dx, config.dy)

    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data = data_t[z, :, :]
        data_cut = grid.extract_vortex_region(data, center_x, center_y, EXTENT)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        c = ax.contour(X_cut, Y_cut, data_cut)
        fig.colorbar(c, ax=ax)
        set_vortex_region_ticks_empty(ax, EXTENT)
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(
            os.path.join(OUTPUT_FOLDER, f"z{str(z).zfill(2)}", f"t{str(config.time_list[t]).zfill(3)}.png")
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
