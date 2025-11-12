# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_grad_p_calc.py
import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid * 1e-3

output_folder = "./data/azim/eq_momentum_u/grad_p/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/ms_pres/t{str(t).zfill(3)}.npy")
    data_rho = np.load(f"./data/azim/ms_rho/t{str(t).zfill(3)}.npy")
    grad_p = - 1 / data_rho[:,1:-1] * (data[:,2:] - data[:,:-2]) / (config.dx * 2)
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", grad_p)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
