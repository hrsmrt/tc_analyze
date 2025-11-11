"""
psi のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/3d/psi_plot.py $style
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

os.makedirs(str(f"./fig/3d/psi/whole_region/"),exist_ok=True)

z_list = [0,9,17,23,29,36,42,48,54,60]
for z in z_list:
  os.makedirs(f"./fig/3d/psi/whole_region/z{str(z).zfill(2)}",exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

def process_t(t):
    data_t = np.load(f"./data/3d/psi/psi_t{str(t).zfill(3)}.npy")
    for z in z_list:
        data = data_t[z,:,:]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3,2.5))
        ax.contour(grid.X, grid.Y,data)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"t={t}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(f"./fig/3d/psi/whole_region/z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(0,config.nt,int(24/config.dt_hour)))
