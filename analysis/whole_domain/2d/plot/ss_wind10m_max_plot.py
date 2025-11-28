"""Plot time series of maximum 10m wind speed."""
# python $WORK/tc_analyze/analysis/whole_domain/2d/plot/ss_wind10m_max_plot.py $style
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

folder = config.get_domain_path("whole_domain", "2d/ss_wind10m_max", data_type="fig")
os.makedirs(folder, exist_ok=True)

# データの読み込み
data = np.load(os.path.join(config.get_domain_path("whole_domain", "2d/ss_wind10m_max"), "ss_wind10m_max.npy"))

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots()
ax.plot(config.time_list[1:], data[1:])
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最大10m風速 [m/s]")
fig.savefig(os.path.join(folder, "ss_wind10m_max.png"))
plt.close()
