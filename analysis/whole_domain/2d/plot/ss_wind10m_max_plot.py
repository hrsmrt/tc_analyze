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
output_folder = config.get_domain_path("whole_domain", "2d/ss_wind10m_max", data_type="fig")
os.makedirs(output_folder, exist_ok=True)

ss_u10m = np.fromfile(f"{config.input_folder}ss_u10m.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)
ss_v10m = np.fromfile(f"{config.input_folder}ss_v10m.grd", dtype=">f4").reshape(
    config.nt, config.ny, config.nx
)

data_abs = np.sqrt(ss_v10m**2 + ss_u10m**2)
data_abs_max = data_abs.max(axis=(1, 2))

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(4, 3))
ax.plot(config.time_list[1:], data_abs_max[1:])
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最大10m風速 [m/s]")
fig.savefig(os.path.join(output_folder, "ss_wind10m_max.png"))
plt.close()
