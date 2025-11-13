# python $WORK/tc_analyze/sums/sums_plot.py varname $style
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

varname = sys.argv[1]

if len(sys.argv) > 2:
    mpl_style_sheet = sys.argv[2]
    plt.style.use(mpl_style_sheet)
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

# ファイルを開いてJSONを読み込む
with open("setting.json", "r", encoding="utf-8") as f:
    setting = json.load(f)
nt = setting["nt"]
dt = setting["dt_output"]
dt_hour = int(dt / 3600)

time_list = [i * dt_hour for i in range(nt)]

folder = f"./fig/sums/"
os.makedirs(folder, exist_ok=True)

# データの読み込み
data = np.load(f"./data/sums/{varname}_sum.npy")

# プロット
plt.plot(time_list[1:], data[1:] * 1e-2)
plt.xlabel("時間 [hour]")
# plt.ylabel("最低海面気圧 [hPa]")
plt.savefig(f"{folder}{varname}_sum.png")
plt.close()
