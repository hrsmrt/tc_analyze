"""
whole_domain_wind_uv_abs のプロット

プロット処理を実行します。
"""

# python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain_wind_uv_abs_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

OUTPUT_FOLDER = config.get_domain_path("whole_domain", "3d/whole_domain_wind_uv_abs", data_type="fig")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_FOLDER, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

u_all = np.memmap(
    f"{config.input_folder}ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
v_all = np.memmap(
    f"{config.input_folder}ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    for z in z_list:
        u = u_all[t, z, :, :]
        v = v_all[t, z, :, :]
        data = np.sqrt(u**2 + v**2)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(2.5, 2))
        c = ax.contourf(
            grid.X,
            grid.Y,
            data,
            cmap="rainbow",
            levels=np.arange(5, 70, 5),
            extend="max",
        )
        fig.colorbar(c, ax=ax)
        ax.set_title(f"t={config.time_list[t]}h, z={round(vgrid[z] * 1e-3, 1):.1f}km")
        ax.set_xticks([0, config.x_width * 1 / 2, config.x_width], ["", "", ""])
        ax.set_yticks([0, config.y_width * 1 / 2, config.y_width], ["", "", ""])
        ax.set_aspect("equal", "box")
        z_folder = os.path.join(OUTPUT_FOLDER, f"z{str(z).zfill(2)}")
        os.makedirs(z_folder, exist_ok=True)
        fig.savefig(
            os.path.join(z_folder, f"t{str(config.time_list[t]).zfill(3)}.png")
        )
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
