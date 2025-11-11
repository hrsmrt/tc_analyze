# nohup python $WORK/tc_analyze/z_profile/hf_plot.py $style
# hf: moist static energy, Nolan+2007 (3)式

import os
import sys
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
from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

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

Parallel(n_jobs=n_jobs)(delayed(process_t)(t) for t in range(config.nt))

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
