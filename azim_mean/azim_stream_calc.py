# python $WORK/tc_analyze/azim_mean/azim_stream_calc.py
# output: 流線関数
# 参考: Smith and Montgomery (2023) 5.61式
# はじめr = 0でz方向に積分し、その後はr方向に積分

import os
import numpy as np
from joblib import Parallel, delayed
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

vgrid = grid.create_vertical_grid()

r_max = 1000e3

nr = int(r_max / config.dx)
R = (np.arange(nr) + 0.5) * config.dx
f = 3.77468e-5

output_folder = "./data/azim/stream/"
os.makedirs(output_folder, exist_ok=True)

def process_t(t):
    rho = np.load(f"./data/azim/ms_rho/t{str(t).zfill(3)}.npy")
    u = np.load(f"./data/azim/wind_relative_radial/t{str(t).zfill(3)}.npy")
    w = np.load(f"./data/azim/ms_w/t{str(t).zfill(3)}.npy")
    phi = np.zeros_like(rho)
    for z in range(1,config.nz):
        phi[z,0] = phi[z-1,0] - 0.5 * (rho[z,0]*u[z,0]*R[0] + rho[z-1,0]*u[z-1,0]*R[0]) * (vgrid[z] - vgrid[z-1])
    for z in range(config.nz):
        for r in range(1,nr):
            phi[z,r] = phi[z,r-1] + 0.5 * (rho[z,r]*w[z,r]*R[r] + rho[z,r-1]*w[z,r-1]*R[r-1]) * (R[r] - R[r-1])

    np.save(f"{output_folder}t{str(t).zfill(3)}.npy", phi)
    print(f"t={t} done")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.nt))
