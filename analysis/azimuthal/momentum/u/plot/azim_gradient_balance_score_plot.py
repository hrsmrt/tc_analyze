# python $WORK/tc_analyze/analysis/azimuthal/momentum/u/plot/azim_gradient_balance_score_plot.py $style
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

# グリッド設定：データから実際のサイズを取得（.npz優先、.npyフォールバック）
sample_data_path = config.get_tc_centric_path("azimuthal", "momentum/u/gradient_balance_score")
sample_npz = os.path.join(sample_data_path, f"t{str(config.t_first).zfill(3)}.npz")
sample_npy = os.path.join(sample_data_path, f"t{str(config.t_first).zfill(3)}.npy")
if os.path.exists(sample_npz):
    sample_npz_data = np.load(sample_npz)
    sample_data = sample_npz_data['data']
elif os.path.exists(sample_npy):
    sample_data = np.load(sample_npy)
else:
    raise FileNotFoundError(f"Neither {sample_npz} nor {sample_npy} found")
nz_data, nr_data = sample_data.shape

# vgrid と rgrid を作成 (shifted cell center: r=1+0.5, 2+0.5, ...)
vgrid = grid.create_vertical_grid()[:nz_data] * 1e-3
rgrid_wall = ((np.arange(nr_data) + 1) * config.dx + config.dx / 2) * 1e-3

X, Y = np.meshgrid(rgrid_wall, vgrid)

output_folder = config.get_tc_centric_path("azimuthal", "momentum/u/gradient_balance_score", data_type="fig")

os.makedirs(output_folder, exist_ok=True)


def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "momentum/u/gradient_balance_score")
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
    c = ax.contourf(
        X, Y, data, cmap="rainbow", levels=np.arange(0, 1.1, 0.1), extend="both"
    )
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_ticks([0, 1])
    ax.set_title(f"傾度風平衡 t = {config.time_list[t]} hour")
    ax.set_ylim([0, 20])
    ax.set_xlabel("半径 [km]")
    ax.set_ylabel("高度 [km]")
    # plt.xticks([0,nr/5-1,nr/5*2-1,nr/5*3-1,nr/5*4-1,nr-1],[int(config.dx*1e-3),int(radius*1e-3/5),int(radius*1e-3/5*2),int(radius*1e-3/5*3),int(radius*1e-3/5*4),int(radius*1e-3)])
    plt.savefig(os.path.join(output_folder, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
