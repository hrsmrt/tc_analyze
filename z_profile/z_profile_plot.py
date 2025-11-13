# python $WORK/tc_analyze/z_profile/z_profile_plot.py varname $style

import os
import sys

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
output_dir = f"./fig/z_profile/whole_domain/{varname}/"
os.makedirs(output_dir, exist_ok=True)

# データの読み込み
data_all = np.load(f"./data/z_profile/z_{varname}.npy")
vgrid = np.loadtxt(config.vgrid_filepath)


def process_t(t):
    data = data_all[t, :]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data, vgrid * 1e-3)
    ax.set_ylabel("z [km]")
    ax.set_xlabel("")
    ax.set_title(f"t = {config.time_list[t]} hour")
    fig.savefig(os.path.join(output_dir, f"t{config.time_list[t]:04d}h.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)

print(f"✅ Saved plots to {output_dir}")
