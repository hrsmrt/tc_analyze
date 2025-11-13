# python $WORK/tc_analyze/sums/sums_calc.py varname
import os
import sys

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig

config = AnalysisConfig()

varname = sys.argv[1]

extent = 500e3
extent_x = int(extent / config.dx)
extent_y = int(extent / config.dy)

z_max = 60

center_x_list = config.center_x
center_y_list = config.center_y

os.makedirs("./data/sums/", exist_ok=True)

x = np.arange(0, config.x_width, config.dx)
y = np.arange(0, config.y_width, config.dy)
X, Y = np.meshgrid(x, y)
X_cut = X[: extent_y * 2, : extent_x * 2]
Y_cut = Y[: extent_y * 2, : extent_x * 2]

data_all = np.memmap(
    f"{config.input_folder}{varname}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    center_x = int(center_x_list[t] / config.dx)
    center_y = int(center_y_list[t] / config.dy)
    x_idx = [(center_x - extent_x + i) % config.nx for i in range(2 * extent_x)]
    y_idx = [(center_y - extent_y + i) % config.ny for i in range(2 * extent_y)]
    data = data_all[t, :z_max, :, :]
    data_cut = data[:, y_idx, :][:, :, x_idx]
    data_sum = data_cut.sum()
    return data_sum


sum_results = Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last)
)

np.save(f"./data/sums/{varname}_sum.npy", sum_results)
