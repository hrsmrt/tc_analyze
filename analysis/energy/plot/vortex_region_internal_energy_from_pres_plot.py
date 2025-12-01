"""
Plot internal energy (e = Cv * p / Rd / ρ) over vortex region.

✅ ストレージ節約版: オンデマンド計算を使用
データを保存せず、必要時に計算することで数GB〜数百GBのストレージを節約

Physics:
- Ideal gas law: p = ρ * Rd * T  →  T = p / (ρ * Rd)
- Internal energy: e = Cv * T = Cv * p / (ρ * Rd)
"""
# python $WORK/tc_analyze/analysis/energy/plot/vortex_region_internal_energy_from_pres_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.basic import Cv, Rd
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

EXTENT = 500e3

center_x_list = config.center_x
center_y_list = config.center_y

OUTPUT_DIR = config.get_tc_centric_path("energy", "internal_energy_from_pres", data_type="fig")
os.makedirs(OUTPUT_DIR, exist_ok=True)

X_cut, Y_cut = grid.get_vortex_region_meshgrid(EXTENT)

z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

# ✅ オンデマンド計算: メモリマップを開く
data_pres = np.memmap(
    f"{config.input_folder}ms_pres.grd",
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
    Process a single time step to create internal energy plots.

    Parameters
    ----------
    t : int
        Time step index
    """
    # ✅ オンデマンド計算: 必要時にその場で計算（保存データ不要）
    p = data_pres[t]  # Pressure [Pa], shape: (nz, ny, nx)
    rho = data_rho[t]  # Density [kg/m³], shape: (nz, ny, nx)

    # 内部エネルギーを計算 e = Cv * p / Rd / ρ [J/kg]
    # 理想気体の状態方程式 p = ρ * Rd * T より T = p / (ρ * Rd)
    # e = Cv * T = Cv * p / (ρ * Rd)
    e = Cv * p / Rd / rho

    center_x = center_x_list[t]
    center_y = center_y_list[t]
    for z in z_list:
        data_cut = grid.extract_vortex_region(e[z], center_x, center_y, EXTENT)
        # === 中心から半径 R 以内のみプロット ===
        R_plot_max = 500e3  # 500 km
        cx = X_cut.mean()  # グリッドの中心を近似
        cy = Y_cut.mean()

        # 半径距離
        R = np.sqrt((X_cut - cx) ** 2 + (Y_cut - cy) ** 2)

        # 半径 R 内だけプロットするマスク
        mask = R <= R_plot_max
        data_masked = np.where(mask, data_cut, np.nan)  # 外側は NaN に
        plt.style.use(mpl_style_sheet)
        fig, ax = plt.subplots(figsize=(3, 2.5))
        c = ax.contourf(X_cut, Y_cut, data_masked, cmap="rainbow", extend="both")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes(
            "right", size="5%", pad=0.1
        )  # size: colorbar幅, pad: 図との距離
        fig.colorbar(c, cax=cax)
        extent_x = int(np.ceil(EXTENT / config.dx))
        extent_y = int(np.ceil(EXTENT / config.dy))
        ax.set_xticks(
            [0, extent_x * config.dx, 2 * extent_x * config.dx],
            ["", "", ""],
        )
        ax.set_yticks(
            [0, extent_y * config.dy, 2 * extent_y * config.dy],
            ["", "", ""],
        )
        ax.set_title(f"t={t:3d}h, z={vgrid[z] * 1e-3:.1f}km")
        ax.set_aspect("equal", "box")
        fig.savefig(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png"))
        plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t)
    for t in range(config.t_first, config.t_last + 1, config.t_step)
)
