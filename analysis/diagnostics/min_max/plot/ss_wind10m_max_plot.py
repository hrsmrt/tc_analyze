"""Plot time series of maximum 10m wind speed."""
# python $WORK/tc_analyze/analysis/diagnostics/min_max/plot/ss_wind10m_max_plot.py $style
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
output_folder = config.get_domain_path("diagnostics", "min_max", data_type="fig")
os.makedirs(output_folder, exist_ok=True)

# データの読み込み (.npz/.npy fallback)
data_path = config.get_domain_path("diagnostics", "min_max")
npz_path = os.path.join(data_path, "ss_wind10m_max.npz")
npy_path = os.path.join(data_path, "ss_wind10m_max.npy")

if os.path.exists(npz_path):
    npz_data = np.load(npz_path)
    data_abs_max = npz_data['data']
elif os.path.exists(npy_path):
    data_abs_max = np.load(npy_path)
else:
    raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(4, 3))
ax.plot(config.time_list[1:], data_abs_max[1:])
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最大10m風速 [m/s]")
fig.savefig(os.path.join(output_folder, "ss_wind10m_max.png"))
plt.close()
