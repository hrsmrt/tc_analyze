"""Plot vertical profile over vortex region for specified variable."""
# python $WORK/tc_analyze/z_profile/vortex_region_plot.py varname $style

import os
import sys

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

varname = sys.argv[1]

# スタイルシートの設定
mpl_style_sheet = parse_style_argument()

# 出力ディレクトリ
output_dir = config.get_fig_path("z_profile", "vortex_region", varname)
os.makedirs(output_dir, exist_ok=True)

# データの読み込み
data_all = np.load(os.path.join(config.get_data_path('z_profile', 'vortex_region'), f"z_{varname}.npy"))
vgrid = np.loadtxt(config.vgrid_filepath)


def process_t(t):
    data = data_all[t, :]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(data, vgrid)
    ax.set_xlim(-15, 15)
    ax.set_ylim(0, 20e3)
    ax.set_ylabel("高度 [km]")
    ax.set_xlabel("")
    ax.set_title(f"t = {config.time_list[t]} hour")
    fig.savefig(os.path.join(output_dir, f"t{config.time_list[t]:04d}h.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)

print(f"✅ Saved plots to {output_dir}")
