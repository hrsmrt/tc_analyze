# python $WORK/tc_analyze/analysis/whole_domain/2d/plot/slp_tppn.py $style
"""
海面気圧（sa_slp）と降水量（sa_tppn）を重ねてプロット

sa_tppn: カスタムrainbowのcontourfで塗りつぶし
sa_slp: 黒いcontourで等高線
"""
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import create_custom_colormap, parse_style_argument

mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

# カスタムカラーマップの作成（下限を白に）
custom_rainbow = create_custom_colormap("rainbow", 3)

# 出力ディレクトリの作成
OUTPUT_DIR = config.get_domain_path("whole_domain", "2d/slp_tppn", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ 高速化: levelsを事前計算（毎回np.arange()を呼ばないように）
TPPN_LEVELS = np.arange(0, 50, 1)
SLP_LEVELS = np.arange(920, 1022, 2)

# データの読み込み（memmap使用）
tppn_memmap = np.memmap(
    f"{config.input_folder}sa_tppn.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)

slp_memmap = np.memmap(
    f"{config.input_folder}sa_slp.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)


def process_t(t):
    # データ読み込み
    tppn_data = tppn_memmap[t]
    slp_data = slp_memmap[t]

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5, 2))

    # 降水量（塗りつぶし）
    cf = ax.contourf(
        grid.X,
        grid.Y,
        tppn_data * 3600,  # kg/m2/s -> mm/h
        levels=TPPN_LEVELS,
        cmap=custom_rainbow,
        extend="both",
    )

    # 海面気圧（黒い線）
    cs = ax.contour(
        grid.X,
        grid.Y,
        slp_data / 100,  # Pa -> hPa
        levels=SLP_LEVELS,
        colors="black",
        linewidths=0.5,
        alpha=0.8,
    )

    # カラーバー（降水量用）
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(cf, cax=cax, label="Precipitation [mm/h]")

    # タイトル
    ax.set_title(f"Precip. & SLP | t={config.time_list[t]:3d}h")

    # 軸の設定
    ax.set_xticks([0, config.x_width / 2, config.x_width], ["", "", ""])
    ax.set_yticks([0, config.y_width / 2, config.y_width], ["", "", ""])
    ax.grid(False)
    ax.set_aspect("equal", "box")

    fig.savefig(os.path.join(OUTPUT_DIR, f"t{str(config.time_list[t]).zfill(4)}.png"))
    plt.close()
    print(f"t={t} done")


# 並列処理
Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)

print(f"✅ 完了: {OUTPUT_DIR}")
