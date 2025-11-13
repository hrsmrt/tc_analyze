# python $WORK/tc_analyze/2d/vortex_region.py varname $style
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_km_empty

VARNAME = sys.argv[1]

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:3] = [1, 1, 1, 1]  # 0に相当する位置（真ん中）を白に変更
custom_rainbow = ListedColormap(colors)

mpl_style_sheet = parse_style_argument()

# 設定の初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

DIR = f"./fig/2d/vortex_region/{VARNAME}/"
os.makedirs(DIR, exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

data_all = np.fromfile(f"{config.input_folder}{VARNAME}.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)


def process_t(t):
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    data = data_all[t]

    data_cut = grid.extract_vortex_region(data, center_x, center_y, EXTENT)
    R_plot_max = 500e3  # 500 km
    cx = X_cut.mean()  # グリッドの中心を近似
    cy = Y_cut.mean()

    # 半径距離
    R = np.sqrt((X_cut - cx) ** 2 + (Y_cut - cy) ** 2)

    # 半径 R 内だけプロットするマスク
    mask = R <= R_plot_max
    data_masked = np.where(mask, data_cut, np.nan)  # 外側は NaN に

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5, 2))
    title = f"t = {config.time_list[t]}h"
    match VARNAME:
        case "sa_albedo":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                levels=np.arange(0, 1.1, 0.1),
                cmap="Greys_r",
            )
            title = "惑星アルベド " + title
        case "sa_cld_frac":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 1.1, 0.1),
                cmap="Blues_r",
            )
            title = "雲被覆率 " + title
        case "sa_cldi":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 10, 0.1),
                cmap=custom_rainbow,
            )
            title = r"鉛直積算雲氷量 [$\mathrm{kg/m^2}$]" + title
        case "ss_cldi":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 10, 0.1),
                cmap=custom_rainbow,
            )
            title = r"鉛直積算雲氷量 [$\mathrm{kg/m^2}$]" + title
        case "sa_cldw":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 10, 0.1),
                cmap=custom_rainbow,
            )
            title = r"鉛直積算雲水量 [$\mathrm{kg/m^2}$]" + title
        case "ss_cldw":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 10, 0.1),
                cmap=custom_rainbow,
            )
            title = r"鉛直積算雲水量 [$\mathrm{kg/m^2}$]" + title
        case "sa_evap":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked * 3600,
                extend="both",
                levels=np.arange(0, 1, 0.1),
                cmap=custom_rainbow,
            )
            title = r"海面蒸発量 [$\mathrm{kg/m^2/h}$]" + title
        case "sa_lh_sfc":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 500, 10),
                cmap=custom_rainbow,
            )
            title = r"潜熱流束 [$\mathrm{W/m^2}$]" + title
        case "sa_sh_sfc":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 100, 5),
                cmap=custom_rainbow,
            )
            title = r"顕熱流束 [$\mathrm{W/m^2}$]" + title
        case "sa_u10m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(-50, 55, 5),
                cmap="bwr",
            )
            title = r"西風 [$\mathrm{m/s}$]" + title
        case "ss_u10m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(-50, 55, 5),
                cmap="bwr",
            )
            title = r"西風 [$\mathrm{m/s}$]" + title
        case "sa_v10m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(-50, 55, 5),
                cmap="bwr",
            )
            title = r"南風 [$\mathrm{m/s}$]" + title
        case "ss_v10m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(-50, 55, 5),
                cmap="bwr",
            )
            title = r"南風 [$\mathrm{m/s}$]" + title
        case "sa_t2m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(297, 303.1, 0.5),
                cmap="rainbow",
            )
            title = r"2m温度 [$\mathrm{K}$]" + title
        case "ss_t2m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(297, 303.1, 0.5),
                cmap="rainbow",
            )
            title = r"2m温度 [$\mathrm{K}$]" + title
        case "sa_q2m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0.015, 0.026, 0.001),
                cmap="rainbow",
            )
            title = r"2m比湿 [$\mathrm{kg/kg}$]" + title
        case "ss_q2m":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0.015, 0.026, 0.001),
                cmap="rainbow",
            )
            title = r"2m比湿 [$\mathrm{kg/kg}$]" + title
        case "sa_vap_atm":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(50, 81, 5),
                cmap="rainbow",
            )
            title = r"可降水量 [$\mathrm{kg/m^2}$]" + title
        case "ss_vap_atm":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(50, 81, 5),
                cmap="rainbow",
            )
            title = r"可降水量 [$\mathrm{kg/m^2}$]" + title
        case "sa_lwu_toa":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(50, 301, 10),
                cmap="rainbow",
            )
            title = r"TOA up. LW flux(all) [$\mathrm{W/m^2}$]" + title
        case "sa_lwu_toa_c":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(50, 301, 10),
                cmap="rainbow",
            )
            title = r"TOA up. LW flux(clear) [$\mathrm{W/m^2}$]" + title
        case "sa_lwd_sfc":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(400, 455, 5),
                cmap="rainbow",
            )
            title = r"SFC dn. LW flux(all) [$\mathrm{W/m^2}$]" + title
        case "sa_lwu_sfc":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(462, 467.1, 0.5),
                cmap="rainbow",
            )
            title = r"SFC dn. LW flux(all) [$\mathrm{W/m^2}$]" + title
        case "sa_swu_toa":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(50, 301, 10),
                cmap="rainbow",
            )
            title = r"TOA up. SW flux(all) [$\mathrm{W/m^2}$]" + title
        case "sa_swd_sfc":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 321, 10),
                cmap="rainbow",
            )
            title = r"SFC dn. SW flux(all) [$\mathrm{W/m^2}$]" + title
        case "sa_swu_sfc":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked,
                extend="both",
                levels=np.arange(0, 15, 1),
                cmap="rainbow",
            )
            title = r"SFC up. SW flux(all) [$\mathrm{W/m^2}$]" + title
        case "sa_slp":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked / 100,
                extend="both",
                levels=np.arange(920, 1022, 2),
                cmap="bwr_r",
            )
            title = "海面気圧 [hPa] " + title
        case "ss_slp":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked / 100,
                extend="both",
                levels=np.arange(920, 1022, 2),
                cmap="bwr_r",
            )
            title = "海面気圧 [hPa] " + title
        case "sa_tppn":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked * 3600,
                levels=np.arange(0, 50, 1),
                extend="both",
                cmap=custom_rainbow,
            )
            title = "降水量 [mm/h] " + title
        case "ss_tppn":
            c = ax.contourf(
                X_cut * 1e-3,
                Y_cut * 1e-3,
                data_masked * 3600,
                levels=np.arange(0, 50, 1),
                extend="both",
                cmap=custom_rainbow,
            )
            title = "降水量 [mm/h] " + title
        case _:
            c = ax.contourf(X_cut * 1e-3, Y_cut * 1e-3, data_masked, cmap="rainbow")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(
        "right", size="5%", pad=0.1
    )  # size: colorbar幅, pad: 図との距離
    fig.colorbar(c, cax=cax)
    set_vortex_region_ticks_km_empty(ax, EXTENT)
    ax.set_title(title)
    ax.set_aspect("equal", "box")
    fig.savefig(f"{DIR}t{str(config.time_list[t]).zfill(3)}.png")
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)
