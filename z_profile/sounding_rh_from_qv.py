# シミュレーションの最後の24hの平均のsounding
# python $PNICAM/analyze/python/z_profile/calc_sounding_pres.py
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "..", "module"))
sys.path.append(module_path)
sys.path.append(os.path.join(script_dir, "../../../database"))
import json
import basic
import numpy as np
import matplotlib.pyplot as plt

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

vgrid = np.loadtxt(f"{script_dir}/../../../database/vgrid/vgrid_c74.txt")

sounding = np.zeros(nz)
sounding_T = np.zeros(nz)
sounding_p = np.zeros(nz)

outdata_dir = "./data/sounding"
outfig_dir = "./fig/sounding"
if not os.path.exists(outdata_dir):
    os.makedirs(outdata_dir)
if not os.path.exists(outfig_dir):
    os.makedirs(outfig_dir)

c = 0
for t in range(nt-int(24/dt_hour),nt):
  c += 1
  for z in range(nz):
    count = nx * ny
    offset = count * (z + t * nz) * 4
    data = np.fromfile("../model/convert/ms_qv.grd",dtype=">f4",count=count,offset=offset)
    data_T = np.fromfile("../model/convert/ms_tem.grd",dtype=">f4",count=count,offset=offset)
    data_p = np.fromfile("../model/convert/ms_pres.grd",dtype=">f4",count=count,offset=offset)
    sounding[z] += np.mean(data)
    sounding_T[z] += np.mean(data_T)
    sounding_p[z] += np.mean(data_p)
sounding /= c
sounding_T /= c
sounding_p /= c

Rd = basic.Rd
Rv = basic.Rv
sounding_rh = np.zeros(nz)
for z in range(nz):
    es = basic.tetens(sounding_T[z])
    ws = (Rd/Rv) * es / (sounding_p[z] - es)
    qs = ws / (1 + ws)
    sounding_rh[z] = sounding[z] / qs

np.savetxt(f"{outdata_dir}/sounding_rh_from_qv.txt", sounding_rh, fmt='%.6f')

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.grid(True)
plt.plot(sounding_rh * 1e2, vgrid * 1e-3, color='black', linewidth=1.0)
plt.xlabel("Relative Humidity [%]")
plt.ylabel("Height [km]")
plt.xticks(np.arange(0, 101, 10))
plt.tight_layout()
plt.savefig(f"{outfig_dir}/sounding_rh_from_qv.png", dpi=300, bbox_inches='tight')
plt.close()
