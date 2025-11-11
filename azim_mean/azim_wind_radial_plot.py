# python $WORK/tc_analyze/azim_mean/azim_wind_radial_plot.py $style
import os
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument(arg_index=1)

config = AnalysisConfig()
grid = GridHandler(config)

radius = 1000e3
nr = int(radius / config.dx)

X, Y = grid.create_radial_vertical_meshgrid(radius)

folder = "./fig/azim/wind_radial/"

os.makedirs(folder,exist_ok=True)

def process_t(t):
  data = np.load(f"./data/azim/wind_radial/t{str(t).zfill(3)}.npy")

  plt.style.use(mpl_style_sheet)
  fig, ax = plt.subplots(figsize=(5,2))
  c = ax.contourf(X,Y,data,cmap="bwr",levels=np.arange(-30,35,5),extend="both")
  cbar = fig.colorbar(c, ax=ax)
  cbar.set_ticks([-30,0,30])
  ax.set_title(f"方位角平均接線風 t = {config.time_list[t]} hour")
  from utils.plotting import set_azimuthal_plot_ticks
  set_azimuthal_plot_ticks(ax, r_max=1000e3, z_max=20e3)
  #ax.set_xlabel("半径 [km]")
  #ax.set_ylabel("高度 [km]")
  plt.savefig(f"{folder}t{str(t).zfill(3)}.png")
  plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
