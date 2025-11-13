# python $WORK/tc_analyze/2d/whole_domain_refactored.py varname $style
"""
全領域の2次元データをプロット

指定された変数の全領域における時系列データをプロットします。
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import PlotConfig, create_custom_colormap, parse_style_argument

# コマンドライン引数の解析
if len(sys.argv) < 2:
    print("使用方法: python whole_domain.py <varname> [style]")
    sys.exit(1)

VARNAME = sys.argv[1]
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

# カスタムカラーマップの作成
custom_rainbow = create_custom_colormap("rainbow", 3)

# 出力ディレクトリの作成
OUTPUT_DIR = f"./fig/2d/whole_domain/{VARNAME}/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# データの読み込み
data_all = np.memmap(
    f"{config.input_folder}{VARNAME}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)

# PlotConfigに追加の変数設定を登録（まだ定義されていない場合）
additional_configs = {
    "sa_slp": {
        "levels": np.arange(990, 1012, 2),
        "cmap": "rainbow",
        "title": r"海面気圧 [$\mathrm{hPa}$]",
        "extend": "both",
    },
    "sa_lwu_toa": {
        "levels": np.arange(220, 321, 10),
        "cmap": "rainbow",
        "title": r"大気上端上向き長波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_lwu_sfc": {
        "levels": np.arange(440, 481, 5),
        "cmap": "rainbow",
        "title": r"地表面上向き長波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_lwd_sfc": {
        "levels": np.arange(400, 461, 10),
        "cmap": "rainbow",
        "title": r"地表面下向き長波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_swu_sfc": {
        "levels": np.arange(0, 110, 10),
        "cmap": "rainbow",
        "title": r"地表面上向き短波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_swd_sfc": {
        "levels": np.arange(200, 441, 40),
        "cmap": "rainbow",
        "title": r"地表面下向き短波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_swu_toa": {
        "levels": np.arange(0, 110, 10),
        "cmap": "rainbow",
        "title": r"大気上端上向き短波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_swd_toa": {
        "levels": np.arange(440, 481, 5),
        "cmap": "rainbow",
        "title": r"大気上端下向き短波放射 [$\mathrm{W/m^2}$]",
        "extend": "both",
    },
    "sa_tppn": {
        "levels": np.arange(0, 50, 1),
        "cmap": custom_rainbow,
        "title": r"降水量 [mm/h]",
        "extend": "both",
        "data_transform": lambda data: data * 3600,
    },
    "ss_tppn": {
        "levels": np.arange(0, 50, 1),
        "cmap": custom_rainbow,
        "title": r"降水量 [mm/h]",
        "extend": "both",
        "data_transform": lambda data: data * 3600,
    },
}

# 追加設定を登録
for var, cfg in additional_configs.items():
    if var not in PlotConfig.VARIABLE_CONFIGS:
        PlotConfig.add_variable(
            var,
            cfg["levels"],
            cfg["cmap"],
            cfg["title"],
            cfg.get("extend", "neither"),
            cfg.get("data_transform"),
        )

# 各時刻のデータをプロット
for t in range(config.t_first, config.t_last):
    data = data_all[t]

    # スタイル適用
    if mpl_style_sheet:
        plt.style.use(mpl_style_sheet)

    fig, ax = plt.subplots(figsize=(2.5, 2))

    # PlotConfigを使用してプロット作成
    try:
        c, title = PlotConfig.create_contourf(
            ax, grid.X, grid.Y, data, VARNAME, config.time_list[t]
        )
    except ValueError:
        # 未定義の変数の場合はデフォルトプロット
        c = ax.contourf(grid.X, grid.Y, data, cmap="rainbow")
        title = f"{VARNAME} t = {config.time_list[t]}h"

    # カラーバーの追加（特定の変数を除く）
    if VARNAME not in ["ss_slp", "sa_slp"]:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        fig.colorbar(c, cax=cax)

    # 軸の設定
    ax.set_xticks([0, config.x_width / 2, config.x_width], ["", "", ""])
    ax.set_yticks([0, config.y_width / 2, config.y_width], ["", "", ""])
    ax.set_title(title)
    ax.grid(False)
    ax.set_aspect("equal", "box")

    # 保存
    fig.savefig(f"{OUTPUT_DIR}t{str(config.time_list[t]).zfill(4)}.png")
    plt.close()

print(f"プロット完了: {OUTPUT_DIR}")
