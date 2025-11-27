# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_stream_max_plot.py $style

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

mpl_style_sheet = parse_style_argument()

output_folder = config.get_fig_path("azim", "stream")
os.makedirs(output_folder, exist_ok=True)

max_phi = []
for t in range(config.t_first, config.t_last + 1):
    data = np.load(os.path.join(config.get_data_path('azim', 'stream'), f"t{str(t).zfill(3)}.npy"))
    print(f"t={t} max: {np.nanmax(data)}")
    max_phi.append(np.nanmax(data))

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5, 2))
plt.plot(config.time_list[config.t_first:config.t_last + 1], max_phi)
ax.set_title("流線関数の最大値")
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("最大値")
fig.savefig(os.path.join(output_folder, "max.png"))
plt.close()
