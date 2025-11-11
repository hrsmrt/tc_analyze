# python $WORK/tc_analyze/azim_mean/eq_momentum_u/azim_du_dr_calc.py
import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig

config = AnalysisConfig()

radius = 1000e3

nr = int(radius / config.dx)

# rgrid generated via grid.create_radial_vertical_meshgrid * 1e-3

output_folder = "./data/azim/eq_momentum_u/du_dr/"

os.makedirs(output_folder,exist_ok=True)

def process_t(t):
    data = np.load(f"./data/azim/wind_relative_radial/t{str(t).zfill(3)}.npy")
    du_dr = (data[:,1:] - data[:,:-1]) / config.dx
    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", du_dr)

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))
