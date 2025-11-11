# python $WORK/tc_analyze/2d/ss_slp_min_plot.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()

# 設定の初期化
config = AnalysisConfig()

folder = f"./fig/center/"
os.makedirs(folder,exist_ok=True)

# データの読み込み
data = np.load(f"./data/ss_slp_min.npy")

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots()
ax.plot(config.time_list[1:], data[1:] * 1e-2)
ax.set_xticks(config.time_ticks)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最低海面気圧 [hPa]")
fig.savefig(f"{folder}ss_slp_min.png")
plt.close()
