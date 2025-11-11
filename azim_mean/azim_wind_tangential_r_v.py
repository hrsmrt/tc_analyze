# python $WORK/tc_analyze/azim_mean/azim_wind_tangential_r_v.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

radius = 1000e3

nr = int(radius / config.dx)

vgrid = grid.create_vertical_grid()
# rgrid generated via grid.create_radial_vertical_meshgrid

X, Y = grid.create_radial_vertical_meshgrid(1000e3)

z_list = [0,9,17,23,29,36,42,48,54,60]

folder = "./fig/azim/wind_tangential/"

os.makedirs(folder,exist_ok=True)
for z in z_list:
  os.makedirs(f"{folder}z{str(z).zfill(2)}",exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/wind_tangential/t{str(t).zfill(3)}.npy")
    for z in z_list:
        folder_z = f"{folder}z{str(z).zfill(2)}/"
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5,2))
        ax.plot(rgrid,data[z])
        ax.set_title(f"方位角平均接線風 t = {config.time_list[t]} hour, z = {vgrid[z]:.1f} km")
        ax.set_ylim([0, 50e3])
        ax.set_yticks([0,10e3,20e3,30e3,40e3,50e3])
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("風速 [m/s]")
        #plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(config.dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
        plt.savefig(f"{folder_z}t{str(t).zfill(3)}.png")
        plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
