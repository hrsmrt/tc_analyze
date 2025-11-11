# python $WORK/tc_analyze/center/ss_slp_center_velocity.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()

x  = np.arange(config.dx*0.5,config.x_width,config.dx)
y  = np.arange(config.dy*0.5,config.y_width,config.dy)
X,Y = np.meshgrid(x,y)

x_c_evo = config.center_x
y_c_evo = config.center_y

x_c_v = np.zeros_like(x_c_evo)
y_c_v = np.zeros_like(y_c_evo)

dx_diff = x_c_evo[2:] - x_c_evo[:-2]
# 周期境界の補正
dx_diff[dx_diff >  config.x_width/2] -= config.x_width
dx_diff[dx_diff < -config.x_width/2] += config.x_width
x_c_v[1:-1] = dx_diff / (2 * config.dt_output)
x_c_v[0] = (x_c_evo[1] - x_c_evo[0]) / (config.dt_output)
x_c_v[-1] = (x_c_evo[-1] - x_c_evo[-2]) / (config.dt_output)

dy_diff = y_c_evo[2:] - y_c_evo[:-2]
# 周期境界の補正
dy_diff[dy_diff >  config.y_width/2] -= config.y_width
dy_diff[dy_diff < -config.y_width/2] += config.y_width
y_c_v[1:-1] = dy_diff / (2 * config.dt_output)
y_c_v[0] = (y_c_evo[1] - y_c_evo[0]) / (config.dt_output)
y_c_v[-1] = (y_c_evo[-1] - y_c_evo[-2]) / (config.dt_output)

for i in range(len(x_c_v)):
    if x_c_v[i] < -config.x_width/(2*config.dt_output):
        x_c_v[i] = config.x_width/config.dt_output + x_c_v[i]

os.makedirs("data/center",exist_ok=True)
os.makedirs("fig/center",exist_ok=True)

np.save("data/center/ss_slp_center_u.npy",x_c_v)
np.save("data/center/ss_slp_center_v.npy",y_c_v)

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5,4))
ax.plot(config.time_list, x_c_v)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("中心移動速度u [m/s]")
fig.savefig("fig/center/ss_slp_center_u.png")

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5,4))
ax.plot(config.time_list, y_c_v)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("中心移動速度v [m/s]")
fig.savefig("fig/center/ss_slp_center_v.png")
