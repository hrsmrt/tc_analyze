# python $WORK/tc_analyze/center/ss_slp_center_calc.py
import numpy as np
import numpy.ma as ma
import json
from joblib import Parallel, delayed

r_max_ite = 100e3

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
triangle_size = setting['triangle_size']
nx = 2 ** glevel
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny

input_folder = setting["input_folder"]

x  = np.arange(dx*0.5,x_width,dx)
y  = np.arange(dy*0.5,y_width,dy)
X,Y = np.meshgrid(x,y)

x_c_evo = np.zeros(nt)
y_c_evo = np.zeros(nt)

time_list = [i * dt_hour for i in range(1,nt)]

data_memmap = np.memmap(
    f"{input_folder}ss_slp.grd",
    dtype=">f4",
    mode="r",
    shape=(nt, ny, nx)
)

def main():
    # 並列実行して結果をリストで受け取る
    results = Parallel(n_jobs=1)(delayed(process_t)(t) for t in range(nt))

    # 結果をそれぞれ x, y に分解
    for t, (x, y) in zip(range(nt), results):
        x_c_evo[t] = x
        y_c_evo[t] = y

    # 保存
    np.savetxt("data/ss_slp_center_x.txt", x_c_evo)
    np.savetxt("data/ss_slp_center_y.txt", y_c_evo)

def process_t(t):
    print(t)
    data = data_memmap[t]
    iy, ix = np.unravel_index(np.argmin(data, axis=None), data.shape)
    x_c = ix * dx + dx * 0.5
    y_c = iy * dy + dy * 0.5
    for i in range(100):
        data_max = data.max()
        x_c_n, y_c_n = iteration(X, Y, data, x_c, y_c, r_max_ite, data_max)
        if (abs(x_c_n - x_c) < dx*1e-2 and abs(y_c_n - y_c) < dy*1e-2):
            break
        x_c = x_c_n
        y_c = y_c_n
        print(i,x_c,y_c)
    return x_c, y_c

def iteration(X, Y, data, x_c, y_c, r_max_ite, data_max):
    dx = (X-x_c)
    dx[dx > x_width*0.5] -= x_width
    dx[dx < -x_width*0.5] += x_width
    dy = Y-y_c

    dist = np.hypot(dx, dy)
    mask = dist <= r_max_ite

    # 重み（例：最大値からの差）。マスク外は 0 に
    w = (data_max - data) * mask
    w_sum = w.sum()
    if w_sum == 0 or not np.isfinite(w_sum):
        # 例外的に重みがゼロや NaN のときは更新せず返す
        return x_c, y_c

    # 変位の重み付き平均を中心に足す（周期で折り返し）
    x_c_new = (x_c + (w * dx).sum() / w_sum)
    if x_c_new < 0:
        x_c_new += x_width
    elif x_c_new >= x_width:
        x_c_new -= x_width
    y_c_new = (y_c + (w * dy).sum() / w_sum)
    if y_c_new < 0:
        y_c_new += y_width
    elif y_c_new >= y_width:
        y_c_new -= y_width
    return x_c_new, y_c_new

if __name__ == "__main__":
    main()
