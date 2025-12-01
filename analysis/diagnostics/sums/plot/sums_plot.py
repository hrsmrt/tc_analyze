# python $WORK/tc_analyze/analysis/diagnostics/sums/plot/sums_plot.py varname $style
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

folder = config.get_tc_centric_path("diagnostics", "sums", data_type="fig")
os.makedirs(folder, exist_ok=True)

# データの読み込み (.npz/.npy fallback)
data_path = config.get_tc_centric_path("diagnostics", "sums")
npz_path = os.path.join(data_path, f"{varname}.npz")
npy_path = os.path.join(data_path, f"{varname}.npy")

if os.path.exists(npz_path):
    npz_data = np.load(npz_path)
    data = npz_data['data']
elif os.path.exists(npy_path):
    data = np.load(npy_path)
else:
    raise FileNotFoundError(f"Neither {npz_path} nor {npy_path} found")

# プロット
plt.style.use(mpl_style_sheet)
plt.plot(config.time_list[config.t_first:config.t_first+len(data)], data * 1e-2)
plt.xlabel("時間 [hour]")
# plt.ylabel("最低海面気圧 [hPa]")
plt.savefig(os.path.join(folder, f"{varname}.png"))
plt.close()
