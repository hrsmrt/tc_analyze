"""Plot 3D divergence field over whole domain."""
# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/divergence_whole_domain_plot.py $style

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)
F = config.f

OUTPUT_DIR = config.get_domain_path("whole_domain", "3d/divergence", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")


def process_t(t):
    """
    Process a single time step to create divergence plots.

    Parameters
    ----------
    t : int
        Time step index
    """
    # データの読み込み (npz/npy fallback)
    data_path_npz = os.path.join(config.get_domain_path("whole_domain", "3d/divergence"), f"div_t{str(t).zfill(3)}.npz")
    data_path_npy = os.path.join(config.get_domain_path("whole_domain", "3d/divergence"), f"div_t{str(t).zfill(3)}.npy")

    if os.path.exists(data_path_npz):
        with np.load(data_path_npz) as npz_data:
            data_z = npz_data['data']
    elif os.path.exists(data_path_npy):
        data_z = np.memmap(
            data_path_npy,
            dtype=np.float32,
            mode="r",
            shape=(config.nz, config.ny, config.nx),
        )
    else:
        raise FileNotFoundError(f"Data file not found: {data_path_npz} or {data_path_npy}")
    X_km, Y_km = grid.get_meshgrid_km()
    for z in z_list:
        data = data_z[z]
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 4))
        c = ax.contourf(
            X_km,
            Y_km,
            data,
            cmap="bwr",
            levels=np.arange(-0.002, 0.0022, 0.0002),
            extend="both",
        )
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(
            "right", size="5%", pad=0.1
        )  # size: colorbar幅, pad: 図との距離
        cbar = fig.colorbar(c, cax=cax)
        cbar.set_ticks([-0.002, 0.002])
        ax.set_title(f"t={config.time_list[t]:3d}h,z={int(vgrid[z] * 1e-2) * 1e-1}km")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        fig.savefig(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
