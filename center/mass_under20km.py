# python $WORK/tc_analyze/center/mass_under20km.py $style
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.normpath(os.path.join(script_dir, "..", "module")))
from joblib import Parallel, delayed

# コマンドライン引数が3つ以上あるかを確認
if len(sys.argv) > 1:
    mpl_style_sheet = sys.argv[1]
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

output_folder = "./fig/center/"
os.makedirs(output_folder, exist_ok=True)

time_list = [t * dt_hour for t in range(nt)]

r_max = 500e3
z_max = 20e3

center_x_list = np.loadtxt("./data/ss_slp_center_x.txt")
center_y_list = np.loadtxt("./data/ss_slp_center_y.txt")

x  = np.arange(0,x_width,dx)
y  = np.arange(0,y_width,dy)
X,Y = np.meshgrid(x,y)

vgrid = np.loadtxt(f"{script_dir}/../../database/vgrid/vgrid_c74.txt")

data_all = np.memmap(f"{input_folder}ms_rho.grd", dtype=">f4", mode="r", shape=(nt,nz,ny,nx))

dz = np.diff(vgrid, prepend=0)  # 層厚 (近似)

mass_list = []

# --- 時間ループ ---
for t in range(nt):
    mask_z = (vgrid <= z_max)
    # --- 質量計算 ---
    # 各格子体積 = dx * dy * dz[z]
    mass_t = 0.0
    for k in range(nz):
        if mask_z[k]:
            rho = data_all[t,k]   # shape = (ny, nx)
            # この高度層の体積要素
            cell_volume = dx * dy * dz[k]   # [m^3]
            mass_t += np.sum(rho) * cell_volume
    print(f"t={t} mass: {mass_t:.3e} kg")
    mass_list.append(mass_t)

# --- プロット ---
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(4,3))

time_h = np.arange(nt) * dt/3600.0   # dt を秒で与えていると仮定して時間[h]に変換
ax.plot(time_h[1:], np.array(mass_list)[1:]/1e14)  # [kg] → [10^14 kg] スケーリング

ax.set_title("Mass z<20km")
ax.set_xlabel("Time [h]")
ax.set_ylabel("Mass [10$^{14}$ kg]")
fig.savefig(f"{output_folder}mass_under20km_time_series.png")
plt.close()
