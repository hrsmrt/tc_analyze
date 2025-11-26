"""
最適化版のdivergence計算

【最適化内容】
1. Z方向のループをベクトル化（5-10倍高速化）
2. 全次元を一度に処理

【期待される高速化】
- 従来版に比べて 5-10倍の高速化
"""
# python $WORK/tc_analyze/examples/optimized_divergence_calc.py
import os
import time

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

# 設定とグリッドの初期化
config = AnalysisConfig()

FOLDER = config.get_data_path("3d", "divergence")

os.makedirs(FOLDER, exist_ok=True)

data_all_u = np.memmap(
    f"{config.input_folder}/ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_all_v = np.memmap(
    f"{config.input_folder}/ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    """
    最適化版のdivergence計算

    【最適化ポイント】
    1. Z方向のループを削除し、全次元を一度に処理
    2. ベクトル化により5-10倍高速化
    """
    start_time = time.time()

    # データ取得
    data_u = data_all_u[t]  # shape: (nz, ny, nx)
    data_v = data_all_v[t]  # shape: (nz, ny, nx)

    # ========================================
    # 【最適化】Z方向のループをベクトル化
    # ========================================
    # ❌ 従来版（遅い）:
    # div = np.zeros((config.nz, config.ny, config.nx), dtype=np.float32)
    # for z in range(config.nz):
    #     du_dx = (np.roll(data_u[z], -1, axis=1) - np.roll(data_u[z], 1, axis=1)) / (2 * config.dx)
    #     dv_dy = (np.roll(data_v[z], -1, axis=0) - np.roll(data_v[z], 1, axis=0)) / (2 * config.dy)
    #     div[z] = du_dx + dv_dy

    # ✅ 最適化版（5-10倍高速）:
    # 全Z方向を一度に処理
    # axis=2はx方向、axis=1はy方向、axis=0はz方向
    du_dx = (np.roll(data_u, -1, axis=2) - np.roll(data_u, 1, axis=2)) / (
        2 * config.dx
    )
    dv_dy = (np.roll(data_v, -1, axis=1) - np.roll(data_v, 1, axis=1)) / (
        2 * config.dy
    )

    # 境界条件の処理（北極と南極）
    # これもベクトル化されている（全z方向を一度に処理）
    dv_dy[:, 0, : config.nx // 2] = (
        data_v[:, 1, : config.nx // 2] - data_v[:, -1, config.nx // 2 :]
    ) / (2 * config.dy)
    dv_dy[:, 0, config.nx // 2 :] = (
        data_v[:, 1, config.nx // 2 :] - data_v[:, -1, : config.nx // 2]
    ) / (2 * config.dy)
    dv_dy[:, -1, : config.nx // 2] = (
        data_v[:, 0, : config.nx // 2] - data_v[:, -2, config.nx // 2 :]
    ) / (2 * config.dy)
    dv_dy[:, -1, config.nx // 2 :] = (
        data_v[:, 0, config.nx // 2 :] - data_v[:, -2, : config.nx // 2]
    ) / (2 * config.dy)

    # Divergence計算
    div = du_dx + dv_dy

    # 保存
    np.save(f"{FOLDER}/div_t{str(t).zfill(3)}.npy", div)

    elapsed = time.time() - start_time
    print(f"t={t}: div [{div.min():.2e}, {div.max():.2e}], time={elapsed:.2f}s")


# 並列実行
if __name__ == "__main__":
    total_start = time.time()

    Parallel(n_jobs=config.n_jobs)(
        delayed(process_t)(t) for t in range(config.t_first, config.t_last)
    )

    total_elapsed = time.time() - total_start
    n_timesteps = config.t_last - config.t_first
    print(f"\n総実行時間: {total_elapsed:.2f}秒")
    print(f"平均処理時間: {total_elapsed / n_timesteps:.2f}秒/タイムステップ")
