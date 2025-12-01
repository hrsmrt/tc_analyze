# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_stream_plot.py $style

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

vgrid = grid.create_vertical_grid()

output_folder = config.get_tc_centric_path("azimuthal", "basic/stream", data_type="fig")
os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "basic/stream")
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")
    # データの形状から半径方向のグリッドを作成
    nr = data.shape[1]
    rgrid = (np.arange(nr) + 0.5) * config.dx
    X, Y = np.meshgrid(rgrid, vgrid)
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 2))
    c = ax.contour(
        X * 1e-3,
        Y * 1e-3,
        data,
        levels=np.arange(0, 1e10, 5e8),
        cmap="rainbow",
        extend="both",
    )
    cbar = fig.colorbar(c, ax=ax)
    # cbar.set_ticks([330,370])
    ax.set_ylim([0, 20e3])
    ax.set_title(f"流線関数 t = {config.time_list[t]} hour")
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    fig.savefig(os.path.join(output_folder, f"t{str(t).zfill(3)}.png"))
    plt.close()
    print(f"t={t} done")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
