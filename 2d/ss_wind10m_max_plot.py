# python $WORK/tc_analyze/analyze/2d/ss_wind10m_max_plot.py $style
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

folder = f"./fig/ss_wind10m/"
os.makedirs(folder,exist_ok=True)

# データの読み込み
data = np.load("./data/ss_wind10m_max.npy")

# プロット
plt.style.use(mpl_style_sheet)
plt.plot(time_list[1:], data[1:])
plt.xlabel("時間 [hour]")
plt.ylabel("最大10m風速 [m/s]")
plt.savefig(f"{folder}ss_wind10m_max.png")
plt.close()
