"""Plot time series of minimum sea level pressure."""
# python $WORK/tc_analyze/analysis/whole_domain/2d/plot/ss_slp_min_plot.py $style
import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()

# 設定の初期化
config = AnalysisConfig()

folder = config.get_fig_path("center")
os.makedirs(folder, exist_ok=True)

# データの読み込み
data = np.load(os.path.join(config.get_data_path(), "ss_slp_min.npy"))

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots()
ax.plot(config.time_list, data * 1e-2)
ax.set_xticks(config.time_ticks)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最低海面気圧 [hPa]")
fig.savefig(os.path.join(folder, "ss_slp_min.png"))
plt.close()
