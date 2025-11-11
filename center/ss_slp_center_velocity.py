# python $WORK/tc_analyze/center/ss_slp_center_velocity.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, ".."))

mpl_style_sheet = sys.argv[1]

from utils.config import AnalysisConfig

config = AnalysisConfig()

time_list = [t * config.dt_hour for t in range(config.nt)]

x  = np.arange(config.dx*0.5,config.x_width,config.dx)
y  = np.arange(config.dy*0.5,config.y_width,config.dy)
X,Y = np.meshgrid(x,y)

x_c_evo = np.loadtxt("data/ss_slp_center_x.txt")
y_c_evo = np.loadtxt("data/ss_slp_center_y.txt")

x_c_v = np.zeros_like(x_c_evo)
y_c_v = np.zeros_like(y_c_evo)

config.dx = x_c_evo[2:] - x_c_evo[:-2]
# 周期境界の補正
config.dx[config.dx >  config.x_width/2] -= config.x_width
config.dx[config.dx < -config.x_width/2] += config.x_width
x_c_v[1:-1] = config.dx / (2 * dt)
x_c_v[0] = (x_c_evo[1] - x_c_evo[0]) / (dt)
x_c_v[-1] = (x_c_evo[-1] - x_c_evo[-2]) / (dt)

config.dy = y_c_evo[2:] - y_c_evo[:-2]
# 周期境界の補正
config.dy[config.dy >  config.y_width/2] -= config.y_width
config.dy[config.dy < -config.y_width/2] += config.y_width
y_c_v[1:-1] = config.dy / (2 * dt)
y_c_v[0] = (y_c_evo[1] - y_c_evo[0]) / (dt)
y_c_v[-1] = (y_c_evo[-1] - y_c_evo[-2]) / (dt)

for i in range(len(x_c_v)):
    if x_c_v[i] < -config.x_width/(2*dt):
        x_c_v[i] = config.x_width/dt + x_c_v[i]

os.makedirs("data/center",exist_ok=True)
os.makedirs("fig/center",exist_ok=True)

np.save("data/center/ss_slp_center_u.npy",x_c_v)
np.save("data/center/ss_slp_center_v.npy",y_c_v)

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5,4))
ax.plot(time_list, x_c_v)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("中心移動速度u [m/s]")
fig.savefig("fig/center/ss_slp_center_u.png")

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(5,4))
ax.plot(time_list, y_c_v)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("中心移動速度v [m/s]")
fig.savefig("fig/center/ss_slp_center_v.png")
