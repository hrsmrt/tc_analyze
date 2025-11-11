"""
python $WORK/tc_analyze/3d/divergence_whole_domain_plot.py $style
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)
f = config.f

output_dir = f"./fig/3d/whole_domain/divergence/"
os.makedirs(output_dir,exist_ok=True)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"{output_dir}z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

def process_t(t):
  data_z = np.memmap(f"./data/3d/divergence/div_t{str(t).zfill(3)}.npy", dtype=np.float32, mode="r", shape=(config.nz, config.ny, config.nx))
  X_km, Y_km = grid.get_meshgrid_km()
  for z in z_list:
    data = data_z[z]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,4))
    c = ax.contourf(X_km, Y_km, data,cmap="bwr", levels=np.arange(-0.002,0.0022,0.0002),extend='both')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(
        "right", size="5%", pad=0.1
    )  # size: colorbar幅, pad: 図との距離
    cbar = fig.colorbar(c, cax=cax)
    cbar.set_ticks([-0.002,0.002])
    ax.set_title(f"t={config.time_list[t]:3d}h,z={int(vgrid[z]*1e-2)*1e-1}km")
    ax.grid(False)
    ax.set_aspect("equal", "box")
    fig.savefig(f"{output_dir}z{str(z).zfill(2)}/t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end,int(24/config.dt_hour)))
