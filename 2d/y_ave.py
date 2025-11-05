# python $WORK/tc_analyze/analyze/2d/y_ave.py varname $style
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))

#from joblib import Parallel, delayed
import json

varname = sys.argv[1]

# コマンドライン引数が3つ以上あるかを確認
if len(sys.argv) > 2:
    mpl_style_sheet = sys.argv[2]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

original_cmap = plt.cm.rainbow
colors = original_cmap(np.linspace(0, 1, 256))  # 元のカラーマップの色を取得
colors[:3] = [1, 1, 1, 1]  # 0に相当する位置（真ん中）を白に変更
custom_rainbow = ListedColormap(colors)

# ファイルを開いてJSONを読み込む
with open("setting.json", "r", encoding="utf-8") as f:
    setting = json.load(f)
glevel = setting["glevel"]
nt = setting["nt"]
dt = setting["dt_output"]
dt_hour = int(dt / 3600)
triangle_size = setting["triangle_size"]
nx = 2**glevel
ny = 2**glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0**0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting["input_folder"]

time_list = [t * dt_hour for t in range(nt)]

dir = f"./fig/2d/y_ave/{varname}/"
os.makedirs(dir, exist_ok=True)

y = np.arange(0, y_width, dy)

data_all = np.memmap(
    f"{input_folder}{varname}.grd", dtype=">f4", mode="r", shape=(nt, ny, nx)
)

for t in range(nt):
    data = data_all[t].mean(axis=1)

    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(2.5,2))
    title = f"t = {time_list[t]}h"
    c = ax.plot(y,data)
    ax.set_title(title)
    ax.set_yticks([0, y_width * 0.25, y_width * 0.5, y_width * 0.75, y_width],["","","","",""])
    # ax.set_xlabel("x [km]")
    # ax.set_ylabel("y [km]")
    fig.savefig(f"{dir}t{str(time_list[t]).zfill(4)}.png")
    plt.close()

#Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))
