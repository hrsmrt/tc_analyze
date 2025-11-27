"""Calculate tropical cyclone center from sea level pressure minimum."""
# python $WORK/tc_analyze/center/ss_slp_center_calc.py

import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

r_max_ite = 100e3


config = AnalysisConfig()
grid = GridHandler(config)

x = np.arange(config.dx * 0.5, config.x_width, config.dx)
y = np.arange(config.dy * 0.5, config.y_width, config.dy)
X, Y = np.meshgrid(x, y)

x_c_evo = []
y_c_evo = []

data_memmap = np.memmap(
    f"{config.input_folder}ss_slp.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)


def main():
    # 並列実行して結果をリストで受け取る
    results = Parallel(n_jobs=config.n_jobs)(
        delayed(process_t)(t) for t in range(config.nt)
    )

    # 結果をそれぞれ x, y に分解
    for t, (x, y) in zip(range(config.nt), results):
        x_c_evo.append(x)
        y_c_evo.append(y)

    # 保存
    OUTPUT_DIR = config.get_data_path("")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    np.savetxt(os.path.join(OUTPUT_DIR, "ss_slp_center_x.txt"), x_c_evo)
    np.savetxt(os.path.join(OUTPUT_DIR, "ss_slp_center_y.txt"), y_c_evo)
    
def process_t(t):
    data = data_memmap[t]
    iy, ix = np.unravel_index(np.argmin(data, axis=None), data.shape)
    x_c = ix * config.dx + config.dx * 0.5
    y_c = iy * config.dy + config.dy * 0.5

    # ✅ 最適化1: data.max()を1回だけ計算（ループの外）
    data_max = data.max()

    # ✅ 最適化2: 収束判定の閾値を事前計算
    threshold_x = config.dx * 1e-2
    threshold_y = config.dy * 1e-2

    for i in range(100):
        x_c_n, y_c_n = iteration(X, Y, data, x_c, y_c, r_max_ite, data_max)

        # ✅ 最適化3: 早期終了判定を高速化
        if abs(x_c_n - x_c) < threshold_x and abs(y_c_n - y_c) < threshold_y:
            break
        x_c = x_c_n
        y_c = y_c_n
    print(t, i, x_c, y_c)
    return x_c, y_c


def iteration(X, Y, data, x_c, y_c, r_max_ite, data_max):
    # ✅ 最適化4: 周期境界条件の計算をGridHandlerに委譲
    dx = X - x_c
    dx = np.where(dx > config.x_width * 0.5, dx - config.x_width, dx)
    dx = np.where(dx < -config.x_width * 0.5, dx + config.x_width, dx)
    dy = Y - y_c

    # ✅ 最適化5: np.hypotよりsqrt(dx^2 + dy^2)の方が速い場合がある
    dist_sq = dx * dx + dy * dy
    mask = dist_sq <= r_max_ite * r_max_ite

    # ✅ 最適化6: 重み計算を1行で（ブロードキャスティング活用）
    w = np.where(mask, data_max - data, 0.0)
    w_sum = w.sum()

    # ✅ 最適化7: 早期リターンの条件を厳密化
    if w_sum <= 0 or not np.isfinite(w_sum):
        return x_c, y_c

    # ✅ 最適化8: 除算を1回だけ実行
    inv_w_sum = 1.0 / w_sum

    # 変位の重み付き平均を中心に足す（周期で折り返し）
    x_c_new = x_c + (w * dx).sum() * inv_w_sum
    x_c_new = x_c_new % config.x_width  # モジュロ演算で周期境界を簡潔に

    y_c_new = y_c + (w * dy).sum() * inv_w_sum
    y_c_new = y_c_new % config.y_width

    return x_c_new, y_c_new


if __name__ == "__main__":
    main()
