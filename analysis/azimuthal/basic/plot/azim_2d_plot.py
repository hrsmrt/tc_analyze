# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_2d_plot.py varname stylesheet
import os
import sys

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

varname = sys.argv[1]
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()

folder = config.get_tc_centric_path("azimuthal", "basic/{varname}", data_type="fig")

os.makedirs(folder, exist_ok=True)


# メインループ
def process_t(t):
    # データの読み込み
    data = np.load(os.path.join(config.get_tc_centric_path("azimuthal", f"basic/{varname}"), f"t{str(t).zfill(3)}.npy"))

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(data)
    ax.set_xlabel("半径 [km]")

    fig.savefig(os.path.join(folder, f"t{str(t).zfill(3)}.png"))
    plt.close()


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
