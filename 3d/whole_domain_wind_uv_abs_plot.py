"""
whole_domain_wind_uv_abs のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/3d/whole_domain_wind_uv_abs_plot.py $style
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

config.time_list = [t * config.dt_hour for t in range(config.nt)]

output_folder = f"./fig/3d/whole_domain/wind_uv_abs/"
os.makedirs(output_folder,exist_ok=True)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"{output_folder}z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

u_all = np.memmap(f"{config.input_folder}ms_u.grd", dtype=">f4", mode="r", shape=(config.nt,config.nz,config.ny,config.nx))
v_all = np.memmap(f"{config.input_folder}ms_v.grd", dtype=">f4", mode="r", shape=(config.nt,config.nz,config.ny,config.nx))

def process_t(t):
    for z in z_list:
        u = u_all[t,z,:,:]
        v = v_all[t,z,:,:]
        data = np.sqrt(u**2 + v**2)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(2.5,2))
        c = ax.contourf(grid.X, grid.Y,data,cmap="rainbow",levels=np.arange(5,70,5),extend='max')
        fig.colorbar(c, ax=ax)
        ax.set_title(f"t={config.time_list[t]}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_xticks([0, config.x_width * 1/2, config.x_width],["","",""])
        ax.set_yticks([0, config.y_width * 1/2, config.y_width],["","",""])
        ax.set_aspect("equal", "box")
        fig.savefig(f"{output_folder}z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(0,config.nt,int(24/config.dt_hour)))
