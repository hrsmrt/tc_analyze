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

folder = config.get_domain_path("whole_domain", "2d/ss_slp_min", data_type="fig")
os.makedirs(folder, exist_ok=True)

# データの読み込み (npz/npy fallback)
data_path_npz = os.path.join(config.get_domain_path("whole_domain", "2d/ss_slp_min"), "ss_slp_min.npz")
data_path_npy = os.path.join(config.get_domain_path("whole_domain", "2d/ss_slp_min"), "ss_slp_min.npy")

if os.path.exists(data_path_npz):
    with np.load(data_path_npz) as npz_data:
        data = npz_data['data']
elif os.path.exists(data_path_npy):
    data = np.load(data_path_npy)
else:
    raise FileNotFoundError(f"Data file not found: {data_path_npz} or {data_path_npy}")

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots()
ax.plot(config.time_list, data * 1e-2)
ax.set_xticks(config.time_ticks)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最低海面気圧 [hPa]")
fig.savefig(os.path.join(folder, "ss_slp_min.png"))
plt.close()
