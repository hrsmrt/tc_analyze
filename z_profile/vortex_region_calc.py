# python $WORK/tc_analyze/z_profile/vortex_region_calc.py varname

from utils.config import AnalysisConfig
import os
import sys

# 実行ファイル（この.pyファイル）を基準に相対パスを指定
import numpy as np
from joblib import Parallel, delayed

varname = sys.argv[1]


config = AnalysisConfig()

output_dir = f"./data/z_profile/vortex_region/"
os.makedirs(output_dir, exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

x = np.arange(0, config.x_width, config.dx) + config.dx / 2
y = np.arange(0, config.y_width, config.dy) + config.dy / 2
X, Y = np.meshgrid(x, y)

R_max = 500e3

# === 入力 ===
data_memmap = np.memmap(
    f"{config.input_folder}{varname}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)

z_profile_all = np.zeros((config.nt, config.nz))


# === 並列処理関数 ===
def process_t(t):
    cx = center_x_list[t]
    cy = center_y_list[t]
    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width
    R = np.sqrt(dX**2 + dY**2)
    iy, ix = np.where(R <= R_max)

    data = data_memmap[t]
    profile = np.mean(data[:, iy, ix], axis=1, dtype=np.float64)

    print(f"t={t:03d}: mean={profile.mean():.3e}")
    return profile


# === 並列実行 ===
results = Parallel(n_jobs=config.n_jobs, verbose=5)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)

# === 結果をまとめる ===
z_profile_all = np.stack(results, axis=0)

# === 保存 ===
os.makedirs(output_dir, exist_ok=True)
np.save(f"{output_dir}z_{varname}.npy", z_profile_all)
print(f"✅ Saved z_profile data for {varname} to {output_dir}z_{varname}.npy")
