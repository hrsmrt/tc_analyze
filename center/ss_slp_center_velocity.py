# python $WORK/tc_analyze/center/ss_slp_center_velocity.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

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

time_list = [t * dt_hour for t in range(nt)]

x  = np.arange(dx*0.5,x_width,dx)
y  = np.arange(dy*0.5,y_width,dy)
X,Y = np.meshgrid(x,y)

x_c_evo = np.loadtxt("data/ss_slp_center_x.txt")
y_c_evo = np.loadtxt("data/ss_slp_center_y.txt")

x_c_v = np.zeros_like(x_c_evo)
y_c_v = np.zeros_like(y_c_evo)

dx = x_c_evo[2:] - x_c_evo[:-2]
# 周期境界の補正
dx[dx >  x_width/2] -= x_width
dx[dx < -x_width/2] += x_width
x_c_v[1:-1] = dx / (2 * dt)
x_c_v[0] = (x_c_evo[1] - x_c_evo[0]) / (dt)
x_c_v[-1] = (x_c_evo[-1] - x_c_evo[-2]) / (dt)

dy = y_c_evo[2:] - y_c_evo[:-2]
# 周期境界の補正
dy[dy >  y_width/2] -= y_width
dy[dy < -y_width/2] += y_width
y_c_v[1:-1] = dy / (2 * dt)
y_c_v[0] = (y_c_evo[1] - y_c_evo[0]) / (dt)
y_c_v[-1] = (y_c_evo[-1] - y_c_evo[-2]) / (dt)

for i in range(len(x_c_v)):
    if x_c_v[i] < -x_width/(2*dt):
        x_c_v[i] = x_width/dt + x_c_v[i]

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
