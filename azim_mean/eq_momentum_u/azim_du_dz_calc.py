# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_du_dz_calc.py
import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid * 1e-3
vgrid = np.loadtxt(f"{script_dir}/../../../database/vgrid/vgrid_c74.txt")

output_folder = "./data/azim/eq_momentum_u/du_dz/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/wind_relative_radial/t{str(t).zfill(3)}.npy")
    du_dz = np.empty((config.nz-1, nr))
    for z in range(config.nz-1):
        du_dz[z,:] = (data[z+1,:] - data[z,:]) / (vgrid[z+1] - vgrid[z])
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", du_dz)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
