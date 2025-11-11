'''
python $WORK/tc_analyze/azim_mean/azim_core_wind_tangential_plot.py $style
中心部のみ
'''
import os
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument(arg_index=1)

radius = 1000e3

nr = int(radius / config.dx)

vgrid = grid.create_vertical_grid()
# rgrid generated via grid.create_radial_vertical_meshgrid

X, Y = grid.create_radial_vertical_meshgrid(1000e3)

folder = "./fig/azim_core/wind_tangential/"

os.makedirs(folder,exist_ok=True)

def process_t(t):
  data = np.load(f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy")

  plt.style.use(mpl_style_sheet)
  fig, ax = plt.subplots(figsize=(5,2))
  c = ax.contourf(X,Y,data,cmap="bwr",levels=np.arange(-30,35,5),extend="both")
  cbar = fig.colorbar(c, ax=ax)
  cbar.set_ticks([-30,0,30])
  ax.set_title(f"方位角平均接線風 t = {config.time_list[t]} hour")
  plt.xlim(0, 150e3)
  plt.ylim(0, 20e3)
  ax.set_xticks([0,50e3,100e3,150e3],["","","",""])
  ax.set_yticks([0,5e3,10e3,15e3,20e3],["","","","",""])
  #ax.set_xlabel("半径 [km]")
  #ax.set_ylabel("高度 [km]")
  ax.set_aspect("equal", "box")
  #plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(config.dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
  plt.savefig(f"{folder}t{str(t).zfill(3)}.png")
  plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
