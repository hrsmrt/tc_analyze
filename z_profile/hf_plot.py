# nohup python $WORK/tc_analyze/z_profile/hf_plot.py $style
# hf: moist static energy, Nolan+2007 (3)式

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

# スタイルシートの設定
mpl_style_sheet = parse_style_argument()

# 出力ディレクトリ
output_dir = "./fig/z_profile/hf/"
os.makedirs(output_dir, exist_ok=True)

# データの読み込み
hf_all = np.load("./data/z_profile/hf.npy")
vgrid = np.loadtxt(config.vgrid_filepath)

# 統計量の計算
ave_all = hf_all.mean(axis=1)
ave_under15 = hf_all[:, vgrid < 15e3].mean(axis=1)

def process_t(t):
    hf = hf_all[t]
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(hf*1e-3, vgrid*1e-3)
    ax.set_ylabel('高度 [km]')
    ax.set_xlabel('湿潤静的エネルギー [kJ/kg]')
    ax.set_title(f't={config.time_list[t]} hour')
    fig.savefig(os.path.join(output_dir, f't{config.time_list[t]:04d}h.png'))
    plt.close()

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end))

# 時系列プロット（全体平均）
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(config.time_list, ave_all * 1e-3)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("湿潤静的エネルギー [kJ/kg]")
fig.savefig(os.path.join(output_dir, "ave_all.png"))
plt.close()

# 時系列プロット（15km以下平均）
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(config.time_list, ave_under15 * 1e-3)
ax.set_xlabel("時間 [hour]")
ax.set_ylabel("湿潤静的エネルギー [kJ/kg]")
fig.savefig(os.path.join(output_dir, "ave_under15.png"))
plt.close()

print(f"✅ Saved plots to {output_dir}")
