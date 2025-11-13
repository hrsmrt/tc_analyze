# シミュレーションの最後の24hの平均のsounding
# python $WORK/analyze/python/z_profile/sounding_rh_from_qv.py $style
import os

import matplotlib.pyplot as plt
import numpy as np

from utils.basic import Rd, Rv, tetens
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

config = AnalysisConfig()
grid = GridHandler(config)

vgrid = grid.create_vertical_grid()

sounding = np.zeros(config.nz)
sounding_T = np.zeros(config.nz)
sounding_p = np.zeros(config.nz)

outdata_dir = "./data/sounding"
outfig_dir = "./fig/sounding"
if not os.path.exists(outdata_dir):
    os.makedirs(outdata_dir)
if not os.path.exists(outfig_dir):
    os.makedirs(outfig_dir)

count_timesteps = 0
for t in range(config.t_last - int(24 / config.dt_hour), config.nt):
    count_timesteps += 1
    for z in range(config.nz):
        count = config.nx * config.ny
        offset = count * (z + t * config.nz) * 4
        data = np.fromfile(
            f"{config.input_folder}ms_qv.grd", dtype=">f4", count=count, offset=offset
        )
        data_T = np.fromfile(
            f"{config.input_folder}ms_tem.grd", dtype=">f4", count=count, offset=offset
        )
        data_p = np.fromfile(
            f"{config.input_folder}ms_pres.grd", dtype=">f4", count=count, offset=offset
        )
        sounding[z] += np.mean(data)
        sounding_T[z] += np.mean(data_T)
        sounding_p[z] += np.mean(data_p)
sounding /= count_timesteps
sounding_T /= count_timesteps
sounding_p /= count_timesteps

sounding_rh = np.zeros(config.nz)
for z in range(config.nz):
    es = tetens(sounding_T[z])
    ws = (Rd / Rv) * es / (sounding_p[z] - es)
    qs = ws / (1 + ws)
    sounding_rh[z] = sounding[z] / qs

np.savetxt(f"{outdata_dir}/sounding_rh_from_qv.txt", sounding_rh, fmt="%.6f")


plt.style.use(parse_style_argument())
fig, ax = plt.subplots(figsize=(3, 5))
ax.plot(sounding_rh * 1e2, vgrid * 1e-3, color="black", linewidth=1.0)
ax.set_xlabel("Relative Humidity [%]")
ax.set_ylabel("Height [km]")
ax.set_xticks(np.arange(0, 101, 10))
plt.savefig(f"{outfig_dir}/sounding_rh_from_qv.png")
plt.close()
