# シミュレーションの最後の24hの平均のsounding
# python $PNICAM/analyze/python/z_profile/calc_sounding_pres.py
import os
import basic
import numpy as np
import matplotlib.pyplot as plt

from utils.config import AnalysisConfig

config = AnalysisConfig()

vgrid = np.loadtxt(config.vgrid_filepath)

sounding = np.zeros(config.nz)
sounding_T = np.zeros(config.nz)
sounding_p = np.zeros(config.nz)

outdata_dir = "./data/sounding"
outfig_dir = "./fig/sounding"
if not os.path.exists(outdata_dir):
    os.makedirs(outdata_dir)
if not os.path.exists(outfig_dir):
    os.makedirs(outfig_dir)

c = 0
for t in range(config.t_last-int(24/config.dt_hour),config.nt):
  c += 1
  for z in range(config.nz):
    count = config.nx * config.ny
    offset = count * (z + t * config.nz) * 4
    data = np.fromfile(f"{config.input_folder}ms_qv.grd",dtype=">f4",count=count,offset=offset)
    data_T = np.fromfile(f"{config.input_folder}ms_tem.grd",dtype=">f4",count=count,offset=offset)
    data_p = np.fromfile(f"{config.input_folder}ms_pres.grd",dtype=">f4",count=count,offset=offset)
    sounding[z] += np.mean(data)
    sounding_T[z] += np.mean(data_T)
    sounding_p[z] += np.mean(data_p)
sounding /= c
sounding_T /= c
sounding_p /= c

Rd = basic.Rd
Rv = basic.Rv
sounding_rh = np.zeros(config.nz)
for z in range(config.nz):
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
