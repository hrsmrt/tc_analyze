# python $WORK/tc_analyze/analysis/azimuthal/eliassen/plot/azim_B_plot.py $style
# Bのi+1/2上の値

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

# グリッド設定：データから実際のビン数を取得
# グリッド設定：データから実際のビン数を取得（.npz優先、.npyフォールバック）
sample_data_path = config.get_tc_centric_path("azimuthal", "eliassen/B")
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

output_folder = config.get_tc_centric_path("azimuthal", "eliassen/B", data_type="fig")
os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "eliassen/B")
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
    c = ax.contourf(r_mesh * 1e-3, z_mesh * 1e-3, data, cmap="rainbow", extend="both")
    cbar = fig.colorbar(c, ax=ax)
    # cbar.set_ticks([300,400])
    ax.set_ylim([0, 20])
    ax.set_title(f"B t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(os.path.join(output_folder, f"t{str(t).zfill(3)}.png"))
    plt.close()
    print(f"t={t} done(max:{data.max()},min:{data.min()})")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
