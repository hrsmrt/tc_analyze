# python $WORK/tc_analyze/azim_mean/eq_momentum_w/azim_grad_p_calc.py
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
vgrid = np.loadtxt(config.vgrid_filepath)

output_folder = "./data/azim/eq_momentum_w/grad_p/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/ms_pres/t{str(t).zfill(3)}.npy")
    data_rho = np.load(f"./data/azim/ms_rho/t{str(t).zfill(3)}.npy")
    grad_p = np.empty((config.nz-1, nr))
    for z in range(config.nz-1):
        grad_p[z,:] = 1 / ((data_rho[z+1,:] + data_rho[z,:]) * 0.5) * (data[z+1,:] - data[z,:]) / (vgrid[z+1] - vgrid[z]) + 9.80665
    
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", grad_p)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
