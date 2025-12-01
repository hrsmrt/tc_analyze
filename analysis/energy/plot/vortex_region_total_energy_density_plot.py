"""
Plot total energy density (ρ * E_total) over vortex region.

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

Physics:
- Total energy per unit mass: E = e + KE + PE [J/kg]
- Total energy per unit volume: ρ * E = ρ * (e + KE + PE) [J/m³]
  - Internal energy density: ρ * e = ρ * Cv * T
  - Kinetic energy density: ρ * KE = (1/2) * ρ * v²
  - Potential energy density: ρ * PE = ρ * g * z
- Energy density (volumetric energy density) in [J/m³]
"""
# python $WORK/tc_analyze/analysis/energy/plot/vortex_region_total_energy_density_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.basic import Cv, g
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

OUTPUT_DIR = config.get_tc_centric_path("energy_density", "total_energy_density", data_type="fig")
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
data_u = np.memmap(
    f"{config.input_folder}ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_v = np.memmap(
    f"{config.input_folder}ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_w = np.memmap(
    f"{config.input_folder}ms_w.grd",
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
    Process a single time step to create total energy density plots.

    Parameters
    ----------
    t : int
        Time step index
    """
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    T = data_tem[t]  # Temperature [K], shape: (nz, ny, nx)
    u = data_u[t]  # Zonal wind [m/s], shape: (nz, ny, nx)
    v = data_v[t]  # Meridional wind [m/s], shape: (nz, ny, nx)
    w = data_w[t]  # Vertical wind [m/s], shape: (nz, ny, nx)
    rho = data_rho[t]  # Density [kg/m³], shape: (nz, ny, nx)

    # 各エネルギー密度成分を計算
    # 内部エネルギー密度 ρ * e = ρ * Cv * T [J/m³]
    e_density = rho * Cv * T

    # 運動エネルギー密度 ρ * KE = (1/2) * ρ * v² [J/m³]
    v_squared = u**2 + v**2 + w**2
    KE_density = 0.5 * rho * v_squared

    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        # 重力ポテンシャルエネルギー密度 ρ * PE = ρ * g * z [J/m³]
        PE_density = rho[z] * g * vgrid[z]

        # 全エネルギー密度 ρ * E_total = ρ * e + ρ * KE + ρ * PE [J/m³]
        E_total_density = e_density[z] + KE_density[z] + PE_density

        data = grid.extract_vortex_region(E_total_density, center_x, center_y, EXTENT)
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(5, 4))
        # データ範囲に基づいてlevelsを自動設定
        vmin, vmax = np.nanmin(data), np.nanmax(data)
        levels = np.linspace(vmin, vmax, 15)
        c = ax.contourf(X_cut * 1e-3, Y_cut * 1e-3, data, levels=levels, cmap="rainbow", extend="both")
        fig.colorbar(c, ax=ax)
        ax.set_title(f"Total Energy Density t={config.time_list[t]:3d}h, z={int(vgrid[z] * 1e-2) * 1e-1}km")
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
