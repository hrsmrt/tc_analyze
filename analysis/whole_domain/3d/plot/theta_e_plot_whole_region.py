"""
theta_e_whole_region のプロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約
"""

# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/theta_e_plot_whole_region.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument
from utils.thermodynamics import calculate_theta_e_from_memmap

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

OUTPUT_DIR = config.get_fig_path("3d", "theta_e", "whole_region")
os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

# ✅ オンデマンド計算: メモリマップを開く
data_tem = np.memmap(
    f"{config.input_folder}ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_pres = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_qv = np.memmap(
    f"{config.input_folder}ms_qv.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    data_t = calculate_theta_e_from_memmap(data_tem, data_pres, data_qv, t)
    for z in z_list:
        data = data_t[z, :, :]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        c = ax.contourf(
            grid.X,
            grid.Y,
            data,
            levels=np.arange(330, 375, 5),
            cmap="rainbow",
            extend="both",
        )
        cbar = fig.colorbar(c, ax=ax)
        cbar.set_ticks([330, 370])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(
            os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}", f"t{str(config.time_list[t]).zfill(3)}.png")
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
