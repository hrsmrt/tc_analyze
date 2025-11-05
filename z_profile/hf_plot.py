# nohup python $WORK/tc_analyze/z_profile/hf_plot.py $WORK/matplotlib/stylesheet/presentation_jp.style &
# hf: moist static energy, Nolan+2007 (3)式

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "..", "module"))
sys.path.append(module_path)
from joblib import Parallel, delayed

# コマンドライン引数が2つ以上あるかを確認
if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    plt.style.use(mpl_style_sheet)
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

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
input_folder = setting['input_folder']

time_list = [t * dt_hour for t in range(nt)]

vgrid = np.loadtxt(script_dir + "/../../database/vgrid/vgrid_c74.txt")

out_dir = "./fig/z_profile/hf/"
os.makedirs(out_dir,exist_ok=True)

ave_all = np.zeros(nt)
ave_under15 = np.zeros(nt)

hf_all = np.load(f"./data/z_profile/hf/hf.npy")

ave_all = hf_all.mean(axis=1)
ave_under15 = hf_all[:,:48].mean(axis=1)

def process_t(t):
    hf = hf_all[t]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(hf*1e-3,vgrid*1e-3)
    ax.set_ylabel('高度 [km]')
    ax.set_xlabel('湿潤静的エネルギー [kJ/kg]')
    ax.set_title(f't={time_list[t]} hour')
    fig.savefig(os.path.join(out_dir, f't{time_list[t]:04d}h.png'))
    plt.close()

Parallel(n_jobs=4)(delayed(process_t)(t) for t in range(nt))


plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(time_list[:], ave_all * 1e-3)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("湿潤静的エネルギー [kJ/kg]")
fig.savefig(os.path.join(out_dir, f"ave_all.png"))
plt.close()

plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(time_list[:], ave_under15 * 1e-3)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("湿潤静的エネルギー [kJ/kg]")
fig.savefig(os.path.join(out_dir, f"ave_under15.png"))
plt.close()
