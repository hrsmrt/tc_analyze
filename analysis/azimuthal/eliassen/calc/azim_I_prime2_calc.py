# python $WORK/tc_analyze/analysis/azimuthal/eliassen/calc/azim_I_prime2_calc.py
# output: I'^2 = \xi (dv/dr + v/r * f)

import os
from datetime import datetime

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
R_wall = (np.arange(1, nr)) * config.dx

# エイリアス（コードの変更を最小限にするため）
f = config.f
pres_s = PRES_S
L = Lv

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/I_prime2")
os.makedirs(output_folder, exist_ok=True)

theta_ref = 300.0  # 基準温位 K


def process_t(t):
    # Load I2 data (.npz優先、.npyフォールバック)
    I2_path = config.get_tc_centric_path('azimuthal', 'eliassen/I2')
    I2_npz = os.path.join(I2_path, f"t{str(t).zfill(3)}.npz")
    I2_npy = os.path.join(I2_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(I2_npz):
        I2_data = np.load(I2_npz)
        I2 = I2_data['data']
    elif os.path.exists(I2_npy):
        I2 = np.load(I2_npy)
    else:
        raise FileNotFoundError(f"Neither {I2_npz} nor {I2_npy} found")

    # Load gamma data (.npz優先、.npyフォールバック)
    gamma_path = config.get_tc_centric_path('azimuthal', 'eliassen/gamma')
    gamma_npz = os.path.join(gamma_path, f"t{str(t).zfill(3)}.npz")
    gamma_npy = os.path.join(gamma_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(gamma_npz):
        gamma_data = np.load(gamma_npz)
        gamma = gamma_data['data']
    elif os.path.exists(gamma_npy):
        gamma = np.load(gamma_npy)
    else:
        raise FileNotFoundError(f"Neither {gamma_npz} nor {gamma_npy} found")

    # Load B data (.npz優先、.npyフォールバック)
    B_path = config.get_tc_centric_path('azimuthal', 'eliassen/B')
    B_npz = os.path.join(B_path, f"t{str(t).zfill(3)}.npz")
    B_npy = os.path.join(B_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(B_npz):
        B_data = np.load(B_npz)
        B = B_data['data']
    elif os.path.exists(B_npy):
        B = np.load(B_npy)
    else:
        raise FileNotFoundError(f"Neither {B_npz} nor {B_npy} found")

    I2_prime = I2 - (gamma[:, 1:] + gamma[:, :-1]) * 0.5 * B
    np.savez(
        os.path.join(output_folder, f"t{str(t).zfill(3)}.npz"),
        data=I2_prime,
        varname="I_prime2",
        method="eliassen_modified_inertial_parameter",
        created_at=datetime.now().isoformat()
    )
    # print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
