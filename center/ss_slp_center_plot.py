# python $WORK/tc_analyze/center/ss_slp_center_plot.py $style
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()

x = np.arange(config.dx * 0.5, config.x_width, config.dx)
y = np.arange(config.dy * 0.5, config.y_width, config.dy)
X, Y = np.meshgrid(x, y)

x_c_evo = config.center_x
y_c_evo = config.center_y

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5, 4))
# colormap と正規化
cmap = cm.rainbow
norm = plt.Normalize(0, config.nt)
# 散布図でプロット
fig, ax = plt.subplots(figsize=(5, 4))
sc = ax.scatter(
    x_c_evo,
    y_c_evo,
    c=np.arange(config.t_first, config.t_last),
    cmap=cmap,
    norm=norm,
    s=20,
)
ax.set_aspect("equal", "box")
ax.set_xlim(0, config.x_width)
ax.set_ylim(0, config.y_width)
ax.set_xticks([0, config.x_width], ["0", int(config.x_width * 1e-3)])
ax.set_yticks([0, config.y_width], ["0", int(config.y_width * 1e-3)])
ax.set_xlabel("x [km]")
ax.set_ylabel("y [km]")
divider = make_axes_locatable(ax)
cax = divider.append_axes(
    "right", size="5%", pad=0.1
)  # size: colorbar幅, pad: 図との距離
plt.colorbar(sc, cax=cax, label="step")
fig.savefig("fig/ss_slp_center.png")
