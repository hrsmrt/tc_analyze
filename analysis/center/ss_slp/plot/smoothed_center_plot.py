"""Plot tropical cyclone center trajectory (smoothed_minimum method).

Plots the trajectory of TC center calculated with smoothed_minimum method.
Reads from smoothed_center.npz (or configured filename in center_configs).

Usage:
    python $WORK/tc_analyze/analysis/center/ss_slp/plot/smoothed_center_plot.py
    python $WORK/tc_analyze/analysis/center/ss_slp/plot/smoothed_center_plot.py dark_background
"""
import os
import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()

# Load smoothed center data
center_dir = config.get_center_path("ss_slp", data_type="data")
filename = config.center_configs.get("ss_slp_smoothed", "smoothed_center.npz")
filepath = os.path.join(center_dir, filename)

if not os.path.exists(filepath):
    raise FileNotFoundError(
        f"Smoothed center file not found: {filepath}\n"
        "Please run: python analysis/center/ss_slp/calc/smoothed.py"
    )

# Load data
data = np.load(filepath)
center = data['center']  # shape: (nt, 2)
x_c_evo = center[:, 0]
y_c_evo = center[:, 1]

# Load metadata
method = data.get('method', 'smoothed_minimum')
r_smooth = data.get('r_smooth', None)
refine_after_smooth = data.get('refine_after_smooth', False)
r_refine = data.get('r_refine', None)
created_at = data.get('created_at', 'Unknown')

x = np.arange(config.dx * 0.5, config.x_width, config.dx)
y = np.arange(config.dy * 0.5, config.y_width, config.dy)
X, Y = np.meshgrid(x, y)

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5, 4))

# colormap と正規化
cmap = 'rainbow'
norm = plt.Normalize(0, config.nt)

# 散布図でプロット
sc = ax.scatter(
    x_c_evo,
    y_c_evo,
    c=np.arange(len(x_c_evo)),
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

# Title with method and parameters
title = "TC Center Trajectory (smoothed_minimum)"
if r_smooth is not None:
    title += f"\nr_smooth={r_smooth*1e-3:.0f}km"
if refine_after_smooth and r_refine is not None:
    title += f", r_refine={r_refine*1e-3:.0f}km"
ax.set_title(title, fontsize=10)

divider = make_axes_locatable(ax)
cax = divider.append_axes(
    "right", size="5%", pad=0.1
)  # size: colorbar幅, pad: 図との距離
plt.colorbar(sc, cax=cax, label="step")

output_dir = config.get_center_path("ss_slp", data_type="fig")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "trajectory_smoothed.png")
fig.savefig(output_path)
plt.close()

print(f"Saved: {output_path}")
print(f"Method: {method}")
if r_smooth is not None:
    print(f"r_smooth: {r_smooth:.0f} m ({r_smooth*1e-3:.1f} km)")
if refine_after_smooth:
    print(f"Refine after smooth: enabled")
    if r_refine is not None:
        print(f"r_refine: {r_refine:.0f} m ({r_refine*1e-3:.1f} km)")
print(f"Created: {created_at}")
