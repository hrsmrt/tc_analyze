# python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_wind10m_tangential_max_plot.py $style
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

folder = config.get_tc_centric_path("azimuthal", "basic/wind10m_tangential", data_type="fig")

os.makedirs(folder, exist_ok=True)

# Load wind10m_tangential_max data (.npz/.npy fallback)
folder_path = config.get_tc_centric_path("azimuthal", "basic/wind10m_tangential")
npz_path_max = os.path.join(folder_path, "wind10m_tangential_max.npz")
npy_path_max = os.path.join(folder_path, "wind10m_tangential_max.npy")

if os.path.exists(npz_path_max):
    npz_data = np.load(npz_path_max)
    wind10m_tangential_max = npz_data['data']
elif os.path.exists(npy_path_max):
    wind10m_tangential_max = np.load(npy_path_max)
else:
    raise FileNotFoundError(f"Neither {npz_path_max} nor {npy_path_max} found")

# Load wind10m_tangential_rmw data (.npz/.npy fallback)
npz_path_rmw = os.path.join(folder_path, "wind10m_tangential_rmw.npz")
npy_path_rmw = os.path.join(folder_path, "wind10m_tangential_rmw.npy")

if os.path.exists(npz_path_rmw):
    npz_data = np.load(npz_path_rmw)
    wind10m_tangential_rmw = npz_data['data']
elif os.path.exists(npy_path_rmw):
    wind10m_tangential_rmw = np.load(npy_path_rmw)
else:
    raise FileNotFoundError(f"Neither {npz_path_rmw} nor {npy_path_rmw} found")

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(config.time_list[1:], wind10m_tangential_max[1:])
ax.set_xlabel("時間 [h]")
ax.set_ylabel("方位角平均最大風速 [m/s]")
fig.savefig(os.path.join(folder, "max.png"))
plt.close()

fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(config.time_list[1:], wind10m_tangential_rmw[1:] * 1e-3)
ax.set_ylim(0, None)
ax.set_xlabel("時間 [h]")
ax.set_ylabel("方位角平均最大風速半径 [km]")
fig.savefig(os.path.join(folder, "rmw.png"))
plt.close()
