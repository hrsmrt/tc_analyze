# python $WORK/tc_analyze/sums/sums_plot.py varname $style
import os
import sys

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()
varname = sys.argv[1]

mpl_style_sheet = parse_style_argument()

folder = config.get_fig_path("sums")
os.makedirs(folder, exist_ok=True)

# データの読み込み
data = np.load(os.path.join(config.get_data_path('sums'), f"{varname}.npy"))

# プロット
plt.style.use(mpl_style_sheet)
plt.plot(config.time_list[config.t_first:config.t_first+len(data)], data * 1e-2)
plt.xlabel("時間 [hour]")
# plt.ylabel("最低海面気圧 [hPa]")
plt.savefig(os.path.join(folder, f"{varname}.png"))
plt.close()
