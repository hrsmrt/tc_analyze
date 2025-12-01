# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_wind_tangential_r_v.py $style
import os

import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

# グリッド設定：データから実際のビン数を取得（.npz優先、.npyフォールバック）
sample_data_path = config.get_tc_centric_path("azimuthal", "basic/wind_tangential")
sample_npz = os.path.join(sample_data_path, f"t{str(config.t_first).zfill(3)}.npz")
sample_npy = os.path.join(sample_data_path, f"t{str(config.t_first).zfill(3)}.npy")
if os.path.exists(sample_npz):
    sample_npz_data = np.load(sample_npz)
    sample_data = sample_npz_data['data']
elif os.path.exists(sample_npy):
    sample_data = np.load(sample_npy)
else:
    raise FileNotFoundError(f"Neither {sample_npz} nor {sample_npy} found")
nr = sample_data.shape[1]
R_MAX = nr * config.dx
rgrid = grid.create_radial_grid(R_MAX)
vgrid = grid.create_vertical_grid()

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]

folder = config.get_tc_centric_path("azimuthal", "basic/wind_tangential", data_type="fig")

os.makedirs(folder, exist_ok=True)
for z in z_list:
    os.makedirs(os.path.join(folder, f"z{str(z).zfill(2)}"), exist_ok=True)


def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "basic/wind_tangential")
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")
    for z in z_list:
        folder_z = os.path.join(folder, f"z{str(z).zfill(2)}")
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 2))
        ax.plot(rgrid, data[z])
        ax.set_title(
            f"方位角平均接線風 t = {config.time_list[t]} hour, z = {vgrid[z]:.1f} km"
        )
        ax.set_ylim([0, 50e3])
        ax.set_yticks([0, 10e3, 20e3, 30e3, 40e3, 50e3])
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("風速 [m/s]")
        plt.savefig(os.path.join(folder_z, f"t{str(t).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
