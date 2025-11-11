# python $WORK/tc_analyze/azim_q8/azim_q8_3d_calc.py varname
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
import numpy as np
from joblib import Parallel, delayed
import json

varname = sys.argv[1]

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
input_folder = setting['input_folder']
n_jobs = setting.get("n_jobs", 1)

r_max = 1000e3

# 格子点座標（m単位）
x = (np.arange(nx) + 0.5) * dx
y = (np.arange(ny) + 0.5) * dy
X, Y = np.meshgrid(x, y)

folder = f"./data/azim_q8/{varname}/"

os.makedirs(folder,exist_ok=True)

center_x_list = config.center_x
center_y_list = config.center_y

# データの読み込み
data_all = np.memmap(f"{input_folder}{varname}.grd", dtype=">f4", mode="r",
                    shape=(nt, nz, ny, nx))

# メインループ
def process_t(t):
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]
    dX = X - cx
    dY = Y - cy
    # 周期境界条件を考慮
    dX = np.where(dX >  x_width / 2, dX - x_width, dX)
    dX = np.where(dX < -x_width / 2, dX + x_width, dX)
    R = np.sqrt(dX ** 2 + dY ** 2)
    mask = R <= r_max
    valid_r = R[mask]

    theta = np.arctan2(dY[mask], dX[mask])
    theta[theta < 0] += 2*np.pi
    theta = (theta - np.pi/2) % (2*np.pi)  # 北を0°にシフト
    sector = (theta // (np.pi/4)).astype(int)   # 0〜7

    bin_idx = (valid_r // dx).astype(int)
    nbins = bin_idx.max() + 1

    # 出力配列 (nz, nbins, 8 sectors)
    azim_sum  = np.zeros((nz, nbins, 8))
    count_r   = np.zeros((nbins, 8), dtype=int)

    data = data_all[t]   # shape = (nz, ny, nx)
    print(f"3d data t: {t}, max: {data.max()}, min: {data.min()}")

    # valid_data は (nz, npoints)
    valid_data = data[:, mask]

    # bin × sector に振り分けて加算
    for i, (b, s) in enumerate(zip(bin_idx, sector)):
        azim_sum[:, b, s] += valid_data[:, i]
        count_r[b, s]     += 1

    # 割り算（ゼロ割回避）
    with np.errstate(divide="ignore", invalid="ignore"):
        azim_mean = np.where(count_r > 0, azim_sum / count_r[np.newaxis, :, :], np.nan)

    print(f"azim mean data t: {t}, max: {np.nanmax(azim_mean)}, min: {np.nanmin(azim_mean)}")

    np.save(f"{folder}t{str(t).zfill(3)}.npy", azim_mean)

Parallel(n_jobs=n_jobs)(delayed(process_t)(t) for t in range(nt))
