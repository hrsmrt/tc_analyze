# python $WORK/tc_analyze/sums/sums_plot.py varname $style
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()
varname = sys.argv[1]

mpl_style_sheet = parse_style_argument()

folder = "./fig/sums/"
os.makedirs(folder, exist_ok=True)

# データの読み込み
data = np.load(f"./data/sums/{varname}_sum.npy")

# プロット
plt.style.use(mpl_style_sheet)
plt.plot(config.time_list[1:], data[1:] * 1e-2)
plt.xlabel("時間 [hour]")
# plt.ylabel("最低海面気圧 [hPa]")
plt.savefig(f"{folder}{varname}_sum.png")
plt.close()
