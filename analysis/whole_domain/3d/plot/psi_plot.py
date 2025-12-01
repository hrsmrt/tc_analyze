"""
Plot streamfunction (psi) field.

✅ ストレージ節約版: オンデマンド計算を使用
渦度データから流線関数を計算し、データ保存不要で数GB〜数百GBのストレージを節約
"""
# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/psi_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument
from utils.streamfunction import calculate_streamfunction

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

OUTPUT_DIR = config.get_domain_path("whole_domain", "3d/psi", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")


def process_t(t):
    # ✅ オンデマンド計算: 渦度から流線関数を計算（保存データ不要）
    # 渦度データを読み込み (npz/npy fallback)
    data_path_npz = os.path.join(config.get_domain_path('whole_domain', '3d/vorticity_z'), f"vor_t{str(t).zfill(3)}.npz")
    data_path_npy = os.path.join(config.get_domain_path('whole_domain', '3d/vorticity_z'), f"vor_t{str(t).zfill(3)}.npy")

    if os.path.exists(data_path_npz):
        with np.load(data_path_npz) as npz_data:
            vorticity_z = npz_data['data']
    elif os.path.exists(data_path_npy):
        vorticity_z = np.load(data_path_npy)
    else:
        raise FileNotFoundError(f"Data file not found: {data_path_npz} or {data_path_npy}")

    # 流線関数を計算
    data_t = calculate_streamfunction(vorticity_z, config.dx, config.dy)
    for z in z_list:
        data = data_t[z, :, :]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        ax.contour(grid.X, grid.Y, data)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"t={t}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(
            os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}", f"t{str(config.time_list[t]).zfill(3)}.png")
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
