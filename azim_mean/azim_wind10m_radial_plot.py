# python $WORK/tc_analyze/azim_mean/azim_wind10m_radial_plot.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed


from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()
config = AnalysisConfig()

folder = f"./fig/azim/wind10m_radial/"

os.makedirs(folder,exist_ok=True)

# メインループ
def process_t(t):
    # データの読み込み
    data = np.load(f"./data/azim/wind10m_radial/t{str(t).zfill(3)}.npy")

    # プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(5,4))
    ax.plot(data)
    ax.set_xlabel("半径 [km]")

    fig.savefig(f"{folder}t{str(t).zfill(3)}.png")
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
