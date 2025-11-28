# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_N2_calc.py
# input: os.path.join(config.get_tc_centric_path('azimuthal', 'basic/buoyancy'), f"t{str(t).zfill(3)}.npy") 温度
# output: N^2 = dB/dz

import os

import numpy as np
from joblib import Parallel, delayed

from utils.basic import PRES_S, Rd, Cp, Lv, g
from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

r_max = 1000e3

nr = int(np.floor(r_max / config.dx))
R = (np.arange(nr) + 0.5) * config.dx
vgrid = grid.create_vertical_grid()

# エイリアス（コードの変更を最小限にするため）
f = config.f
pres_s = PRES_S
L = Lv

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/N2")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    b = np.load(os.path.join(config.get_tc_centric_path('azimuthal', 'eliassen/buoyancy'), f"t{str(t).zfill(3)}.npy"))

    # ベクトル化版（従来のforループより10-100倍高速）
    # 従来版: for z in range(config.nz - 1): db_dz[z, :] = (b[z + 1, :] - b[z, :]) / (vgrid[z + 1] - vgrid[z])
    db_dz = (b[1:, :] - b[:-1, :]) / (vgrid[1:, np.newaxis] - vgrid[:-1, np.newaxis])
    db_dz = db_dz.astype(np.float32)

    np.save(os.path.join(output_folder, f"t{str(t).zfill(3)}.npy"), db_dz)
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
