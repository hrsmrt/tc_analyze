"""
Plot internal energy density (ρ * e = ρ * Cv * T) over vortex region.

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

Physics:
- Internal energy per unit mass: e = Cv * T [J/kg]
- Internal energy per unit volume: ρ * e = ρ * Cv * T [J/m³]
- Energy density (volumetric energy density) in [J/m³]
"""
# python $WORK/tc_analyze/analysis/energy/plot/vortex_region_internal_energy_density_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.basic import Cv
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, set_vortex_region_ticks_empty

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

OUTPUT_DIR = config.get_tc_centric_path("energy_density", "internal_energy_density", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

# ✅ オンデマンド計算: メモリマップを開く
data_tem = np.memmap(
    f"{config.input_folder}ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_rho = np.memmap(
    f"{config.input_folder}ms_rho.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    """
    Process a single time step to create internal energy density plots.

    Parameters
    ----------
    t : int
        Time step index
    """
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    T = data_tem[t]  # Temperature [K], shape: (nz, ny, nx)
    rho = data_rho[t]  # Density [kg/m³], shape: (nz, ny, nx)

    # 内部エネルギー密度を計算 ρ * e = ρ * Cv * T [J/m³]
    e_density = rho * Cv * T

    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data = grid.extract_vortex_region(e_density[z], center_x, center_y, EXTENT)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 4))
        c = ax.contourf(X_cut * 1e-3, Y_cut * 1e-3, data, cmap="rainbow", extend="both")
        fig.colorbar(c, ax=ax)
        ax.set_title(f"Internal Energy Density t={config.time_list[t]:3d}h, z={int(vgrid[z] * 1e-2) * 1e-1}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.grid(False)
        ax.set_aspect("equal", "box")
        set_vortex_region_ticks_empty(ax, EXTENT)
        fig.savefig(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
