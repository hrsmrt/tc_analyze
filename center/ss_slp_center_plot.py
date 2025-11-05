# python $WORK/tc_analyze/center/ss_slp_center_plot.py $style
import os
import sys
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

import json

mpl_style_sheet = sys.argv[1]

# ファイルを開いてJSONを読み込む
with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
triangle_size = setting['triangle_size']
nx = 2 ** glevel
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny

x  = np.arange(dx*0.5,x_width,dx)
y  = np.arange(dy*0.5,y_width,dy)
X,Y = np.meshgrid(x,y)

x_c_evo = np.loadtxt("data/ss_slp_center_x.txt")
y_c_evo = np.loadtxt("data/ss_slp_center_y.txt")


plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5,4))
# colormap と正規化
cmap = cm.rainbow
norm = plt.Normalize(0, nt)
# 散布図でプロット
fig, ax = plt.subplots(figsize=(5,4))
sc = ax.scatter(x_c_evo, y_c_evo, c=np.arange(nt), cmap=cmap, norm=norm, s=20)
ax.set_aspect('equal', 'box')
ax.set_xlim(0,x_width)
ax.set_ylim(0,y_width)
ax.set_xticks([0,x_width],["0",int(x_width*1e-3)])
ax.set_yticks([0,y_width],["0",int(y_width*1e-3)])
ax.set_xlabel("x [km]")
ax.set_ylabel("y [km]")
divider = make_axes_locatable(ax)
cax = divider.append_axes(
        "right", size="5%", pad=0.1
    )  # size: colorbar幅, pad: 図との距離
plt.colorbar(sc, cax=cax, label="step")
fig.savefig("fig/ss_slp_center.png")
