# python $WORK/tc_analyze/center/mass_under20km.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

config = AnalysisConfig()

output_folder = "./fig/center/"
os.makedirs(output_folder, exist_ok=True)

r_max = 500e3
z_max = 20e3

center_x_list = config.center_x
center_y_list = config.center_y

x  = np.arange(0,config.x_width,config.dx)
y  = np.arange(0,config.y_width,config.dy)
X,Y = np.meshgrid(x,y)

vgrid = np.loadtxt(f"{config.vgrid_filepath}")

data_all = np.memmap(f"{config.input_folder}ms_rho.grd", dtype=">f4", mode="r", shape=(config.nt,config.nz,config.ny,config.nx))

dz = np.diff(vgrid, prepend=0)  # 層厚 (近似)

mass_list = []

# --- 時間ループ ---
for t in range(config.nt):
    mask_z = (vgrid <= z_max)
    # --- 質量計算 ---
    # 各格子体積 = config.dx * config.dy * dz[z]
    mass_t = 0.0
    for k in range(config.nz):
        if mask_z[k]:
            rho = data_all[t,k]   # shape = (config.ny, config.nx)
            # この高度層の体積要素
            cell_volume = config.dx * config.dy * dz[k]   # [m^3]
            mass_t += np.sum(rho) * cell_volume
    print(f"t={t} mass: {mass_t:.3e} kg")
    mass_list.append(mass_t)

# --- プロット ---
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(4,3))

ax.plot(config.time_list[1:], np.array(mass_list)[1:]/1e14)  # [kg] → [10^14 kg] スケーリング

ax.set_title("Mass z<20km")
ax.set_xlabel("Time [h]")
ax.set_ylabel("Mass [10$^{14}$ kg]")
fig.savefig(f"{output_folder}mass_under20km_time_series.png")
plt.close()
