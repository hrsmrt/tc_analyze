"""
10m風の方位角平均動径風のプロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

python $WORK/tc_analyze/azim_mean/azim_wind10m_radial_plot.py $style
"""
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_wind10m
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()
config = AnalysisConfig()
grid = GridHandler(config)

folder = config.get_fig_path("azim", "wind10m_radial")

os.makedirs(folder, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# ✅ オンデマンド計算: メモリマップを開く (2D)
data_u = np.memmap(
    f"{config.input_folder}ss_u10m.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)
data_v = np.memmap(
    f"{config.input_folder}ss_v10m.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)


# メインループ
def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    data, _ = calculate_azimuthal_mean_wind10m(
        data_u, data_v, t, center_x_list, center_y_list, grid
    )

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(data)
    ax.set_xlabel("半径 [km]")

    fig.savefig(os.path.join(folder, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
