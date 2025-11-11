# python $WORK/tc_analyze/center/mass_all.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
from joblib import Parallel, delayed

# コマンドライン引数が3つ以上あるかを確認
if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")

from utils.config import AnalysisConfig

config = AnalysisConfig()

output_folder = "./fig/center/"
os.makedirs(output_folder, exist_ok=True)

time_list = [t * config.dt_hour for t in range(config.nt)]

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

x  = np.arange(0,config.x_width,config.dx)
y  = np.arange(0,config.y_width,config.dy)
X,Y = np.meshgrid(x,y)

vgrid = np.loadtxt(f"{setting['vgrid_filepath']}")

data_all = np.memmap(f"{config.input_folder}ms_rho.grd", dtype=">f4", mode="r", shape=(config.nt,config.nz,config.ny,config.nx))

dz = np.diff(vgrid, prepend=0)  # 層厚 (近似)

mass_list = []

# --- 時間ループ ---
for t in range(config.nt):
    # --- 質量計算 ---
    # 各格子体積 = config.dx * config.dy * dz[z]
    mass_t = 0.0
    for k in range(config.nz):
        rho = data_all[t,k]   # shape = (config.ny, config.nx)
        # この高度層の体積要素
        cell_volume = config.dx * config.dy * dz[k]   # [m^3]
        mass_t += np.sum(rho) * cell_volume
    print(f"t={t} mass: {mass_t:.3e} kg")
    mass_list.append(mass_t)

# --- プロット ---
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(4,3))

time_h = np.arange(config.nt) * dt/3600.0   # dt を秒で与えていると仮定して時間[h]に変換
ax.plot(time_h[1:], np.array(mass_list)[1:]/1e14)  # [kg] → [10^14 kg] スケーリング

ax.set_title("Mass whole region")
ax.set_xlabel("Time [h]")
ax.set_ylabel("Mass [10$^{14}$ kg]")
fig.savefig(f"{output_folder}mass_whole_region_time_series.png")
plt.close()
