"""
vortex_region_r250

解析処理を実行します。
"""

# python $WORK/tc_analyze/3d/vortex_region_r250.py varname $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
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

config.time_list = [t * config.dt_hour for t in range(config.nt)]

extent = 250e3

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

output_folder = f"./fig/3d/vortex_region_r250/{varname}/"
os.makedirs(output_folder,exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(extent)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"{output_folder}z{str(z).zfill(2)}",exist_ok=True)

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
            case "ms_rh":
                c = ax.contourf(X_cut,Y_cut,data_masked,levels=np.arange(0,1.2,0.1),cmap="rainbow",extend="both")
            case _:
                c = ax.contourf(X_cut,Y_cut,data_masked,cmap="rainbow")
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
        #ax.set_xlabel("x [km]")
        #ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")
        fig.savefig(f"{output_folder}z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(0,config.nt,int(24/config.dt_hour)))
