"""

config = AnalysisConfig()
grid = GridHandler(config)

python $WORK/tc_analyze/azim_mean/azim_dyn_radial_plot.py $style
"""

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_azimuthal_plot_ticks

config = AnalysisConfig()
grid = GridHandler(config)
mpl_style_sheet = parse_style_argument()

# グリッド設定：データから実際のビン数を取得（.npz優先、.npyフォールバック）
sample_data_path = config.get_tc_centric_path("azimuthal", "basic/dyn_radial")
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
r_mesh, z_mesh = grid.create_radial_vertical_meshgrid(R_MAX)

folder = config.get_tc_centric_path("azimuthal", "basic/dyn_radial", data_type="fig")

os.makedirs(folder, exist_ok=True)


def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "basic/dyn_radial")
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contourf(r_mesh, z_mesh, data, cmap="bwr", levels=np.linspace(-0.01, 0.01, 21))
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_ticks([-0.01, 0, 0.01])
    ax.set_title(f"方位角平均 dyn d動径風 t = {config.time_list[t]} hour")
    set_azimuthal_plot_ticks(ax, r_max=R_MAX, z_max=20e3)
    # ax.set_xlabel("半径 [km]")
    # ax.set_ylabel("高度 [km]")
    plt.savefig(os.path.join(folder, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
