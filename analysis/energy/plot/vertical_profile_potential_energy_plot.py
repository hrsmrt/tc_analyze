"""Plot gravitational potential energy vertical profile.

Physics:
- Gravitational potential energy per unit mass: PE = g * z
- This is a simple linear function of height
- Useful for comparing with internal and kinetic energy magnitudes
"""
# python $WORK/tc_analyze/analysis/energy/plot/vertical_profile_potential_energy_plot.py $style

import os

import matplotlib
matplotlib.use('Agg')  # GUI描画のオーバーヘッド削減
import matplotlib.pyplot as plt
import numpy as np

from utils.basic import g
from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

config = AnalysisConfig()

# スタイルシートの設定
mpl_style_sheet = parse_style_argument()

# 出力ディレクトリ
output_dir = config.get_domain_path("energy", "vertical_profile/potential_energy", data_type="fig")
os.makedirs(output_dir, exist_ok=True)

# 鉛直グリッドの読み込み
vgrid = np.loadtxt(config.vgrid_filepath)

# ポテンシャルエネルギーの計算 PE = g * z [J/kg]
PE = g * vgrid

# プロット
plt.style.use(mpl_style_sheet)
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(PE * 1e-3, vgrid * 1e-3, linewidth=2)
ax.set_ylabel("高度 [km]")
ax.set_xlabel("重力ポテンシャルエネルギー [kJ/kg]")
ax.set_title("Gravitational Potential Energy Vertical Profile (PE = g·z)")
ax.grid(True, alpha=0.3)

# 参考値を追加
ax.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='10 km')
ax.axhline(y=15, color='orange', linestyle='--', alpha=0.5, label='15 km')
ax.legend()

fig.savefig(os.path.join(output_dir, "potential_energy_profile.png"))
plt.close()

print(f"Potential energy profile saved to: {output_dir}/potential_energy_profile.png")

# テキストファイルにも出力
output_file = os.path.join(output_dir, "potential_energy_profile.txt")
with open(output_file, 'w') as f:
    f.write("# Gravitational Potential Energy Vertical Profile\n")
    f.write("# PE = g * z\n")
    f.write(f"# g = {g} m/s^2\n")
    f.write("#\n")
    f.write("# Height [m]    Height [km]    PE [J/kg]    PE [kJ/kg]\n")
    for z, pe in zip(vgrid, PE):
        f.write(f"{z:12.2f}  {z*1e-3:12.3f}  {pe:12.2f}  {pe*1e-3:12.3f}\n")

print(f"Potential energy data saved to: {output_file}")

# 統計情報の出力
print("\n=== Potential Energy Statistics ===")
print(f"Minimum PE (surface):     {PE.min()*1e-3:.3f} kJ/kg at z = {vgrid[PE.argmin()]*1e-3:.3f} km")
print(f"Maximum PE (top):         {PE.max()*1e-3:.3f} kJ/kg at z = {vgrid[PE.argmax()]*1e-3:.3f} km")
print(f"PE at 10 km:              {g*10e3*1e-3:.3f} kJ/kg")
print(f"PE at 15 km:              {g*15e3*1e-3:.3f} kJ/kg")
print(f"PE at tropopause (~12km): {g*12e3*1e-3:.3f} kJ/kg")
