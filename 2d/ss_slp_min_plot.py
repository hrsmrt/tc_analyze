# python $WORK/tc_analyze/2d/ss_slp_min_plot.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json

if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)

time_list = [i * dt_hour for i in range(nt)]
time_ticks = [i * dt_hour for i in range(0, nt, 24)]

folder = f"./fig/center/"
os.makedirs(folder,exist_ok=True)

# データの読み込み
data = np.load(f"./data/ss_slp_min.npy")

# プロット
plt.style.use(mpl_style_sheet)
plt.plot(time_list[1:], data[1:] * 1e-2)
plt.xticks(time_ticks)
plt.xlabel("時間 [hour]")
plt.ylabel("最低海面気圧 [hPa]")
plt.savefig(f"{folder}ss_slp_min.png")
plt.close()
