# python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_max_plot.py $style
import os

import matplotlib.pyplot as plt
import numpy as np

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)
mpl_style_sheet = parse_style_argument()

folder = f"./fig/azim/wind10m_tangential/"

os.makedirs(folder, exist_ok=True)

wind10m_tangential_max = np.load(
    f"./data/azim/wind10m_tangential/wind10m_tangential_max.npy"
)
wind10m_tangential_rmw = np.load(
    f"./data/azim/wind10m_tangential/wind10m_tangential_rmw.npy"
)

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(config.time_list[1:], wind10m_tangential_max[1:])
ax.set_xlabel("時間 [h]")
ax.set_ylabel("方位角平均最大風速 [m/s]")
fig.savefig(f"{folder}max.png")
plt.close()

fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(config.time_list[1:], wind10m_tangential_rmw[1:] * 1e-3)
ax.set_ylim(0, None)
ax.set_xlabel("時間 [h]")
ax.set_ylabel("方位角平均最大風速半径 [km]")
fig.savefig(f"{folder}rmw.png")
plt.close()
