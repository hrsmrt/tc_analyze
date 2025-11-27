"""Plot 3D data over whole domain with two different z-levels overlaid (filled + line)."""
# python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py varname z1 z2 $style [sigma]
# 例: python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_tem 0 36 $style
# 例（smooth化）: python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_tem 0 36 $style 2.0
import os
import sys

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import gaussian_filter

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

VARNAME = sys.argv[1]
Z1 = int(sys.argv[2])  # 下の面（塗りつぶし）
Z2 = int(sys.argv[3])  # 上の面（線のcontour）

# Smooth化パラメータの解析（最後の引数がfloatならsigma値）
SIGMA = 0.0  # デフォルトはsmooth化なし
if len(sys.argv) >= 5:
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
    OUTPUT_DIR = config.get_fig_path("3d", "whole_domain_two_levels_filled", os.path.join(VARNAME, f"_z{Z1}_z{Z2}_smooth{SIGMA:.1f}"))
else:
    OUTPUT_DIR = config.get_fig_path("3d", "whole_domain_two_levels_filled", os.path.join(VARNAME, f"_z{Z1}_z{Z2}"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

x_axis = np.arange(0.5 * config.dx, config.nx * config.dx, config.dx)
y_axis = np.arange(0.5 * config.dy, config.ny * config.dy, config.dy)
X, Y = np.meshgrid(x_axis, y_axis)

# ✅ I/O最適化: memmapを使用
data_memmap = np.memmap(
    f"{config.input_folder}{VARNAME}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def get_contour_settings(varname, z_level):
    """変数名とZ面に応じたcontourの設定を返す"""
    settings = {
        'levels': None,
        'cmap': 'rainbow',
        'extend': 'both'
    }

    match varname:
        case "ms_u" | "ms_v":
            settings['levels'] = np.arange(-40, 45, 5)
            settings['cmap'] = 'bwr'
        case "ms_w":
            settings['levels'] = np.arange(-4, 4.5, 0.5)
            settings['cmap'] = 'bwr'
        case "ms_tem":
            if z_level == 0:
                settings['levels'] = np.arange(295, 305, 1)
            else:
                settings['levels'] = None
            settings['cmap'] = 'rainbow'
        case "ms_rh":
            settings['levels'] = np.arange(0, 1.2, 0.1)
            settings['cmap'] = 'rainbow'
        case "ms_qv":
            if z_level == 0:
                settings['levels'] = np.arange(0.005, 0.027, 0.002)
            else:
                settings['levels'] = None
            settings['cmap'] = 'rainbow'

    return settings


def process_t(t):
    # 2つのZ面のデータを読み込み
    data1 = data_memmap[t, Z1, :, :].copy()
    data2 = data_memmap[t, Z2, :, :].copy()

    # Smooth化を適用
    if SIGMA > 0:
        data1 = gaussian_filter(data1, sigma=SIGMA)
        data2 = gaussian_filter(data2, sigma=SIGMA)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(6, 4.5))

    # 下の面（Z1）: 塗りつぶしcontour
    settings1 = get_contour_settings(VARNAME, Z1)
    if settings1['levels'] is not None:
        cf = ax.contourf(
            X, Y, data1,
            levels=settings1['levels'],
            cmap=settings1['cmap'],
            extend=settings1['extend'],
            alpha=0.8
        )
    else:
        cf = ax.contourf(X, Y, data1, cmap=settings1['cmap'], extend='both', alpha=0.8)

    # カラーバー
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    fig.colorbar(cf, cax=cax, label=f'z={vgrid[Z1] * 1e-3:.1f}km')

    # 上の面（Z2）: 線のcontour
    settings2 = get_contour_settings(VARNAME, Z2)
    if settings2['levels'] is not None:
        # 線の数を減らして見やすくする
        levels2 = settings2['levels'][::2] if len(settings2['levels']) > 10 else settings2['levels']
        cs = ax.contour(
            X, Y, data2,
            levels=levels2,
            colors='black',
            linewidths=1.5,
            linestyles='solid',
            alpha=0.9
        )
    else:
        cs = ax.contour(X, Y, data2, colors='black', linewidths=1.5, alpha=0.9)

    # タイトル
    title = (
        f"t={config.time_list[t]:3d}h | "
        f"Fill: z={vgrid[Z1] * 1e-3:.1f}km | "
        f"Line: z={vgrid[Z2] * 1e-3:.1f}km"
    )
    if SIGMA > 0:
        title += f" | Smoothed (σ={SIGMA:.1f})"
    ax.set_title(title)

    # 軸の設定
    ax.set_xticks([0, config.x_width / 2, config.x_width], ["", "", ""])
    ax.set_yticks([0, config.y_width / 2, config.y_width], ["", "", ""])
    ax.grid(False)
    ax.set_aspect("equal", "box")

    # 凡例を追加
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor=plt.colormaps[settings1['cmap']](0.5), alpha=0.8,
              label=f'z={vgrid[Z1] * 1e-3:.1f}km (fill)'),
        Line2D([0], [0], color='black', linewidth=1.5,
               label=f'z={vgrid[Z2] * 1e-3:.1f}km (line)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)

    fig.savefig(os.path.join(OUTPUT_DIR, f"t{str(t).zfill(3)}.png"), bbox_inches='tight')
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)

print(f"✅ 完了: {OUTPUT_DIR}")
