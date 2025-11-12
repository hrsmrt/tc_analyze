# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_coriolis_plot.py $style
import os
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

radius = 1000e3

nr = int(radius / config.dx)


X, Y = grid.create_radial_vertical_meshgrid(1000e3)

output_folder = "./fig/azim/eq_momentum_u/coriolis/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
  data = np.load(f"./data/azim/eq_momentum_u/coriolis/t{str(t).zfill(3)}.npy")

  plt.style.use(mpl_style_sheet)
  fig, ax = plt.subplots(figsize=(5,2))
  c = ax.contourf(X,Y,data,cmap="bwr",levels=np.arange(-0.005,0.0055,0.0005),extend="both")
  cbar = fig.colorbar(c, ax=ax)
  cbar.set_ticks([-0.005,0,0.005])
  ax.set_title(f"コリオリ力 t = {config.time_list[t]} hour")
  ax.set_ylim([0, 20])
  ax.set_xlabel("半径 [km]")
  ax.set_ylabel("高度 [km]")
  #plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(config.dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
  plt.savefig(f"{output_folder}t{str(t).zfill(3)}.png")
  plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
