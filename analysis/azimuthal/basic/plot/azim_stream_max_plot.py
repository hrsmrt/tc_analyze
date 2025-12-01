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

output_folder = config.get_tc_centric_path("azimuthal", "basic/stream", data_type="fig")
os.makedirs(output_folder, exist_ok=True)

max_phi = []
for t in range(config.t_first, config.t_last + 1):
    # データの読み込み（.npz優先、.npyフォールバック）
    data_path = config.get_tc_centric_path("azimuthal", "basic/stream")
    npz_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npz")
    npy_path = os.path.join(data_path, f"t{str(t).zfill(3)}.npy")

    if os.path.exists(npz_path):
        npz_data = np.load(npz_path)
        data = npz_data['data']
    elif os.path.exists(npy_path):
        data = np.load(npy_path)
    else:
        raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")
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
