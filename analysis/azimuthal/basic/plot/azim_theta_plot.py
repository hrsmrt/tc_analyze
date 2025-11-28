"""
温位の方位角平均プロット

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

python $WORK/tc_analyze/azim_mean/azim_theta_plot.py $style
"""

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.azimuthal import calculate_azimuthal_mean_theta
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

vgrid = np.loadtxt(config.vgrid_filepath)

output_folder = config.get_tc_centric_path("azimuthal", "basic/theta", data_type="fig")
os.makedirs(output_folder, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

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


def process_t(t):
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    data = calculate_azimuthal_mean_theta(
        data_tem, data_pres, t, center_x_list, center_y_list, grid
    )
    # データの形状から半径方向のグリッドを作成
    nr = data.shape[1]
    xgrid = np.arange(nr) * config.dx
    X, Y = np.meshgrid(xgrid, vgrid)
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(
        X, Y, data, levels=np.arange(300, 405, 10), cmap="rainbow", extend="both"
    )
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_ticks([300, 400])
    ax.set_ylim([0, 20e3])
    ax.set_title(f"相当温位 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(os.path.join(output_folder, f"t{str(t).zfill(3)}.png"))
    plt.close()
    print(f"t={t} done(max:{data.max()},min:{data.min()})")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
