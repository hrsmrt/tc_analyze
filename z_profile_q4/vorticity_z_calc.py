# python $WORK/tc_analyze/z_profile_q4/vorticity_z_calc.py

import os

import numpy as np

from utils.config import AnalysisConfig
from utils.grid import GridHandler

config = AnalysisConfig()
grid = GridHandler(config)

output_dir = "./data/z_profile_q4/zeta/"

center_x_list = config.center_x
center_y_list = config.center_y

R_max = 300e3

# --- 出力配列 (config.nt, config.nz, 4象限) ---
z_profile_q = np.zeros((config.nt, config.nz, 4))

for t in range(config.t_first, config.t_last):
    # 3Dデータを読み込む (nz, ny, nx)
    data_3d = np.load(f"./data/3d/vorticity_z/vor_t{str(t).zfill(3)}.npy")

    cx = center_x_list[t]
    cy = center_y_list[t]

    # 周期境界条件を考慮した距離計算
    R = grid.calculate_radial_distance(cx, cy)

    # --- マスク（半径R_max以内）---
    mask_R = R <= R_max

    # --- 方位角 θ (北を0°, 半時計回りに増加) ---
    theta = grid.calculate_theta(cx, cy)
    theta = (theta + np.pi / 2) % (2 * np.pi)  # 北=0, 東=90°, 南=180°, 西=270°

    # --- 象限番号 (0: 北東, 1: 南東, 2: 南西, 3: 北西) ---
    sector = np.floor(theta / (np.pi / 2)).astype(int)  # 0〜3

    for z in range(config.nz):
        data = data_3d[z, :, :]

        # 半径R_max内のみ
        data_masked = np.where(mask_R, data, np.nan)

        # 象限ごとの平均
        for q in range(4):
            q_mask = sector == q
            vals = data_masked[q_mask]
            if np.isfinite(vals).any():
                z_profile_q[t, z, q] = np.nanmean(vals)
            else:
                z_profile_q[t, z, q] = np.nan

    print(f"Processed time step t={t}")

# --- 保存 ---
os.makedirs(output_dir, exist_ok=True)
np.save(f"{output_dir}z_zeta_quadrants.npy", z_profile_q)
print(f"✅ Saved quadrant profiles for zeta to {output_dir}z_zeta_quadrants.npy")
