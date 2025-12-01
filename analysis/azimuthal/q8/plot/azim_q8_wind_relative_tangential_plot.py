# python $WORK/tc_analyze/analysis/azimuthal/q8/plot/azim_q8_wind_relative_tangential_plot.py $style
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
sample_data_path = config.get_tc_centric_path("azimuthal", "q8/wind_relative_tangential")
sample_npz = os.path.join(sample_data_path, f"t{str(config.t_first).zfill(3)}.npz")
sample_npy = os.path.join(sample_data_path, f"t{str(config.t_first).zfill(3)}.npy")
if os.path.exists(sample_npz):
    sample_npz_data = np.load(sample_npz)
    sample_data = sample_npz_data['data']
elif os.path.exists(sample_npy):
    sample_data = np.load(sample_npy)
else:
    raise FileNotFoundError(f"Neither {sample_npz} nor {sample_npy} found")
nz_data, nr, n_sectors = sample_data.shape
R_MAX = nr * config.dx

# rgrid と vgrid を作成
rgrid = (np.arange(nr) + 0.5) * config.dx * 1e-3  # km単位
vgrid = grid.create_vertical_grid() * 1e-3  # km単位

X, Y = np.meshgrid(rgrid, vgrid)

folder = config.get_tc_centric_path("azimuthal", "q8/wind_relative_tangential", data_type="fig")

os.makedirs(folder, exist_ok=True)

sector_names = [f"sector{s}" for s in range(8)]


def process_t(t):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "q8/wind_relative_tangential")
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")
    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

    # 各sectorごとにプロット
    for s in range(8):
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 2))
        data_s = data[:, :, s]
        if t < 96:
            c = ax.contourf(
                X, Y, data_s, cmap="bwr", levels=np.arange(-30, 35, 5), extend="both"
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-30, 0, 30])
        else:
            c = ax.contourf(
                X, Y, data_s, cmap="bwr", levels=np.arange(-60, 70, 10), extend="both"
            )
            cbar = fig.colorbar(c, ax=ax)
            cbar.set_ticks([-60, 0, 60])
        ax.set_ylim([0, 20])
        ax.set_title(f"{sector_names[s]} 接線風速 t = {config.time_list[t]} hour")
        ax.set_xlabel("半径 [km]")
        ax.set_ylabel("高度 [km]")

        sec_folder = os.path.join(folder, sector_names[s])
        os.makedirs(sec_folder, exist_ok=True)
        fig.savefig(os.path.join(sec_folder, f"t{str(t).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
