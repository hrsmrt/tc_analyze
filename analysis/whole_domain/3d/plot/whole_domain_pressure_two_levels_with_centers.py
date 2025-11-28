"""Plot pressure at two z-levels with line contours and overlay 5 ms_pres centers."""
# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain_pressure_two_levels_with_centers.py z1 z2 z_center1 z_center2 z_center3 z_center4 z_center5 $style
# 例: python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain_pressure_two_levels_with_centers.py 0 36 0 9 17 23 29 $style
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# 引数の解析
Z1 = int(sys.argv[1])  # 1つ目のZ面（contour用）
Z2 = int(sys.argv[2])  # 2つ目のZ面（contour用）
Z_CENTERS = [int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
             int(sys.argv[6]), int(sys.argv[7])]  # 中心をプロットする5つのZ面

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化（3D中心座標を使用）
config = AnalysisConfig(center_type="3d", center_path="center/ms_pres")
grid = GridHandler(config)

# 出力ディレクトリ
z_center_str = "_".join([f"z{z}" for z in Z_CENTERS])
OUTPUT_DIR = config.get_fig_path(
    "3d", "whole_domain_pressure_two_levels_with_centers",
    f"z{Z1}_z{Z2}_centers_{z_center_str}"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

x_axis = np.arange(0.5 * config.dx, config.nx * config.dx, config.dx)
y_axis = np.arange(0.5 * config.dy, config.ny * config.dy, config.dy)
X, Y = np.meshgrid(x_axis, y_axis)

# データ読み込み（ms_pres固定）
data_memmap = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)

# 中心座標の読み込み（3D: shape (nt, nz)）
center_x_3d = config.center_x  # shape: (nt, nz)
center_y_3d = config.center_y  # shape: (nt, nz)

# 中心プロット用のカラーとマーカー設定
CENTER_COLORS = ['red', 'orange', 'yellow', 'green', 'cyan']
CENTER_MARKERS = ['x', '+', '*', 'o', 's']


def process_t(t):
    # 2つのZ面のpressureデータを読み込み
    data1 = data_memmap[t, Z1, :, :].copy()
    data2 = data_memmap[t, Z2, :, :].copy()

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(7, 5.5))

    # 1つ目のZ面（線のcontour - 赤色）
    levels1 = np.arange(90000, 105000, 1000)  # 圧力レベル [Pa]
    cs1 = ax.contour(
        X, Y, data1,
        levels=levels1,
        colors='darkred',
        linewidths=1.5,
        linestyles='solid',
        alpha=0.7
    )
    ax.clabel(cs1, inline=True, fontsize=8, fmt='%d')

    # 2つ目のZ面（線のcontour - 青色）
    levels2 = np.arange(90000, 105000, 1000)  # 圧力レベル [Pa]
    cs2 = ax.contour(
        X, Y, data2,
        levels=levels2,
        colors='darkblue',
        linewidths=1.5,
        linestyles='solid',
        alpha=0.7
    )
    ax.clabel(cs2, inline=True, fontsize=8, fmt='%d')

    # 5層の中心位置をプロット
    for i, z_center in enumerate(Z_CENTERS):
        c_x = center_x_3d[t, z_center]
        c_y = center_y_3d[t, z_center]
        ax.plot(
            c_x, c_y,
            marker=CENTER_MARKERS[i],
            color=CENTER_COLORS[i],
            markersize=10,
            markeredgewidth=2,
            label=f'Center z={vgrid[z_center] * 1e-3:.1f}km'
        )

    # タイトル
    title = (
        f"Pressure | t={config.time_list[t]:3d}h | "
        f"Red: z={vgrid[Z1] * 1e-3:.1f}km | "
        f"Blue: z={vgrid[Z2] * 1e-3:.1f}km"
    )
    ax.set_title(title, fontsize=10)

    # 軸の設定
    ax.set_xticks([0, config.x_width / 2, config.x_width], ["", "", ""])
    ax.set_yticks([0, config.y_width / 2, config.y_width], ["", "", ""])
    ax.grid(False)
    ax.set_aspect("equal", "box")

    # 凡例を追加
    ax.legend(loc='upper right', fontsize=8, ncol=2)

    fig.savefig(
        os.path.join(OUTPUT_DIR, f"t{str(t).zfill(3)}.png"),
        bbox_inches='tight',
        dpi=150
    )
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)

print(f"✅ 完了: {OUTPUT_DIR}")
