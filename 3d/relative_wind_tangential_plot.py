"""
relative_wind_tangential のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/3d/relative_wind_tangential_plot.py $style
import os
import numpy as np
import matplotlib.pyplot as plt

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument
from joblib import Parallel, delayed

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

extent = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

os.makedirs(str(f"./fig/3d/vortex_region/tangential_wind_radial/"),exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(extent)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"./fig/3d/vortex_region/relative_wind_tangential/z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

def process_t(t):
    data_t = np.load(f"./data/3d/relative_wind_tangential/t{str(t).zfill(3)}.npy")
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data = data_t[z,:,:]
        data_cut = grid.extract_vortex_region(data, center_x, center_y, extent)
        # === 中心から半径 R 以内のみプロット ===
        R_plot_max = 500e3  # 500 km
        cx = X_cut.mean()  # グリッドの中心を近似
        cy = Y_cut.mean()

        # 半径距離
        R = np.sqrt((X_cut - cx)**2 + (Y_cut - cy)**2)

        # 半径 R 内だけプロットするマスク
        mask = R <= R_plot_max
        data_masked = np.where(mask, data_cut, np.nan)  # 外側は NaN に
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3,2.5))
        c = ax.contourf(X_cut,Y_cut,data_masked,cmap="bwr",levels=np.arange(-30,35,5),extend='both')
        fig.colorbar(c, ax=ax)
        extent_x = int(np.ceil(extent / config.dx))
        extent_y = int(np.ceil(extent / config.dy))
        ax.set_xticks(
                [0, extent_x * config.dx, 2 * extent_x * config.dx],
                [-int(extent*1e-3), "0", int(extent*1e-3)],
            )
        ax.set_yticks(
            [0, extent_y * config.dy, 2 * extent_y * config.dy],
            [int(extent*1e-3), "0", -int(extent*1e-3)],
        )
        ax.set_title(f"t={t}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")
        fig.savefig(f"./fig/3d/vortex_region/relative_wind_tangential/z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end,int(24/config.dt_hour)))
