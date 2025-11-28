"""Plot ss_slp with ms_pres at specified z-level, overlay both centers.

Visualizes sea-level pressure (ss_slp) with filled contour and overlays
ms_pres at a specified z-level with line contour. Displays both centers.

Usage:
    python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain_slp_with_ms_pres_level.py z_ms_pres $style [sigma]

Example:
    python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain_slp_with_ms_pres_level.py 17 $style
    python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain_slp_with_ms_pres_level.py 23 $style 2.0
"""
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import gaussian_filter

from utils.center import load_center_coordinates
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# 引数の解析
Z_MS_PRES = int(sys.argv[1])  # ms_presのZ面

# Smooth化パラメータの解析（最後の引数がfloatならsigma値）
SIGMA = 0.0  # デフォルトはsmooth化なし
if len(sys.argv) >= 3:
    try:
        SIGMA = float(sys.argv[-1])
        # sigma値を指定した場合、最後の引数を除外してスタイルを解析
        sys.argv = sys.argv[:-1]
    except ValueError:
        # floatに変換できない場合はsigma=0.0のまま
        pass

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

# 出力ディレクトリ（smooth化の有無で分ける）
if SIGMA > 0:
    OUTPUT_DIR = config.get_domain_path("whole_domain", f"3d/whole_domain_slp_with_ms_pres_level/z{Z_MS_PRES}_smooth{SIGMA:.1f}", data_type="fig")
else:
    OUTPUT_DIR = config.get_domain_path("whole_domain", f"3d/whole_domain_slp_with_ms_pres_level/z{Z_MS_PRES}", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

x_axis = np.arange(0.5 * config.dx, config.nx * config.dx, config.dx)
y_axis = np.arange(0.5 * config.dy, config.ny * config.dy, config.dy)
X, Y = np.meshgrid(x_axis, y_axis)

# データ読み込み
# ss_slp: 2D (nt, ny, nx)
ss_slp_memmap = np.memmap(
    f"{config.input_folder}ss_slp.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)

# ms_pres: 3D (nt, nz, ny, nx)
ms_pres_memmap = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)

# 中心座標の読み込み
# ss_slp center: 2D (nt, 2)
ss_slp_center_x, ss_slp_center_y, ss_slp_meta = load_center_coordinates(config, "ss_slp")

# ms_pres center: 3D (nt, nz, 2)
ms_pres_center_x, ms_pres_center_y, ms_pres_meta = load_center_coordinates(config, "ms_pres")


def process_t(t):
    # データの読み込み
    ss_slp_data = ss_slp_memmap[t, :, :].copy()
    ms_pres_data = ms_pres_memmap[t, Z_MS_PRES, :, :].copy()

    # Smooth化を適用
    if SIGMA > 0:
        ss_slp_data = gaussian_filter(ss_slp_data, sigma=SIGMA)
        ms_pres_data = gaussian_filter(ms_pres_data, sigma=SIGMA)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))

    # ss_slp: 塗りつぶしcontour
    levels_slp = np.arange(990, 1012, 1)  # 海面気圧レベル [hPa]
    cf = ax.contourf(
        X, Y, ss_slp_data * 1e-2,  # Pa -> hPa
        levels=levels_slp,
        cmap='rainbow',
        extend='both',
        alpha=0.7
    )

    # カラーバー
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(cf, cax=cax, label='SS SLP [hPa]')

    # ms_pres: 線のcontour（levelsは自動）
    cs_ms = ax.contour(
        X, Y, ms_pres_data * 1e-2,  # Pa -> hPa
        colors='black',
        linewidths=1.5,
        linestyles='solid',
        alpha=0.9
    )

    # ss_slp中心をプロット
    ax.plot(
        ss_slp_center_x[t], ss_slp_center_y[t],
        marker='x',
        color='red',
        markersize=12,
        markeredgewidth=3,
        label='SS SLP Center'
    )

    # ms_pres中心をプロット（指定されたz面）
    ax.plot(
        ms_pres_center_x[t, Z_MS_PRES], ms_pres_center_y[t, Z_MS_PRES],
        marker='o',
        color='blue',
        markersize=10,
        markeredgewidth=2,
        markerfacecolor='none',
        label=f'MS PRES Center z={vgrid[Z_MS_PRES] * 1e-3:.1f}km'
    )

    # タイトル
    title = (
        f"Pressure | t={config.time_list[t]:3d}h | "
        f"Filled: SS SLP | "
        f"Contour: MS PRES z={vgrid[Z_MS_PRES] * 1e-3:.1f}km"
    )
    if SIGMA > 0:
        title += f" | σ={SIGMA:.1f}"
    ax.set_title(title, fontsize=10)

    # 軸の設定
    ax.set_xticks([0, config.x_width / 2, config.x_width], ["", "", ""])
    ax.set_yticks([0, config.y_width / 2, config.y_width], ["", "", ""])
    ax.grid(False)
    ax.set_aspect("equal", "box")

    # 凡例を追加
    ax.legend(loc='upper right', fontsize=9)

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
