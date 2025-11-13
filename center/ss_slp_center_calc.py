# python $WORK/tc_analyze/center/ss_slp_center_calc.py
from utils.config import AnalysisConfig
import numpy as np
from joblib import Parallel, delayed

r_max_ite = 100e3


config = AnalysisConfig()

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
    np.savetxt("data/ss_slp_center_x.txt", x_c_evo)
    np.savetxt("data/ss_slp_center_y.txt", y_c_evo)


def process_t(t):
    data = data_memmap[t]
    iy, ix = np.unravel_index(np.argmin(data, axis=None), data.shape)
    x_c = ix * config.dx + config.dx * 0.5
    y_c = iy * config.dy + config.dy * 0.5
    for i in range(100):
        data_max = data.max()
        x_c_n, y_c_n = iteration(X, Y, data, x_c, y_c, r_max_ite, data_max)
        if abs(x_c_n - x_c) < config.dx * 1e-2 and abs(y_c_n - y_c) < config.dy * 1e-2:
            break
        x_c = x_c_n
        y_c = y_c_n
    print(t, i, x_c, y_c)
    return x_c, y_c


def iteration(X, Y, data, x_c, y_c, r_max_ite, data_max):
    dx = X - x_c
    dx[dx > config.x_width * 0.5] -= config.x_width
    dx[dx < -config.x_width * 0.5] += config.x_width
    dy = Y - y_c

    dist = np.hypot(dx, dy)
    mask = dist <= r_max_ite

    # 重み（例：最大値からの差）。マスク外は 0 に
    w = (data_max - data) * mask
    w_sum = w.sum()
    if w_sum == 0 or not np.isfinite(w_sum):
        # 例外的に重みがゼロや NaN のときは更新せず返す
        return x_c, y_c

    # 変位の重み付き平均を中心に足す（周期で折り返し）
    x_c_new = x_c + (w * dx).sum() / w_sum
    if x_c_new < 0:
        x_c_new += config.x_width
    elif x_c_new >= config.x_width:
        x_c_new -= config.x_width
    y_c_new = y_c + (w * dy).sum() / w_sum
    if y_c_new < 0:
        y_c_new += config.y_width
    elif y_c_new >= config.y_width:
        y_c_new -= config.y_width
    return x_c_new, y_c_new


if __name__ == "__main__":
    main()
