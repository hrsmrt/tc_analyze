"""
vortex_region

解析処理を実行します。
"""

# python $WORK/tc_analyze/3d/vortex_region.py varname $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

varname = sys.argv[1]

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

extent = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

os.makedirs(str(f"./fig/3d/vortex_region/{varname}/"),exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(extent)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"./fig/3d/vortex_region/{varname}/z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

data_all = np.memmap(f"{config.input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(config.nt,config.nz,config.ny,config.nx))

def process_t(t):
    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data = data_all[t,z,:,:]
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
        match varname:
            case "ms_u":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(-40,45,5),cmap="bwr",extend="both")
            case "ms_v":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(-40,45,5),cmap="bwr",extend="both")
            case "ms_w":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(-4,4.5,0.5),cmap="bwr",extend="both")
            case "ms_tem":
                if z == 0:
                    c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(295,305,1),cmap="rainbow",extend="both")
                else:
                    c = ax.contourf(X_cut,Y_cut,data_masked,cmap="rainbow",extend="both")
            case "ms_rh":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(0,1.2,0.1),cmap="rainbow",extend="both")
            case "ms_qv":
                if z == 0:
                    c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(0.005,0.027,0.002),cmap="rainbow",extend="both")
                else:
                    c = ax.contourf(X_cut,Y_cut,data_masked,cmap="rainbow",extend="both")
            case _:
                c = ax.contourf(X_cut,Y_cut,data_masked,cmap="rainbow")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(
            "right", size="5%", pad=0.1
        )  # size: colorbar幅, pad: 図との距離
        fig.colorbar(c, cax=cax)
        extent_x = int(np.ceil(extent / config.dx))
        extent_y = int(np.ceil(extent / config.dy))
        ax.set_xticks(
                [0, extent_x * config.dx, 2 * extent_x * config.dx],
                ["","",""],
            )
        ax.set_yticks(
            [0, extent_y * config.dy, 2 * extent_y * config.dy],
            ["","",""],
        )
        ax.set_title(f"t={t:3d}h, z={vgrid[z]*1e-3:.1f}km")
        #ax.set_xlabel("x [km]")
        #ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")
        fig.savefig(f"./fig/3d/vortex_region/{varname}/z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last,int(24/config.dt_hour)))
