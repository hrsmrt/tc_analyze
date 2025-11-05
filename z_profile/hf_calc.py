# python $WORK/tc_analyze/z_profile/hf_calc.py
# hf: moist static energy, Nolan+2007 (3)式

import os
import sys
import json
import numpy as np
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.normpath(os.path.join(script_dir, "..", "..", "module"))
sys.path.append(module_path)
from joblib import Parallel, delayed

cp = 1004 # J/kg/K
L = 2.5e6 # J/kg, An introduction to clouds, Table 2.1(温度依存性あり)
Lv = 2.8e6 # J/kg, An introduction to clouds, Table 2.1(温度依存性あり)
g = 9.81 # m/s

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

out_dir = "./data/z_profile/hf/"
os.makedirs(out_dir,exist_ok=True)

T = np.zeros(nz) # K, Temperature
ms_qv = np.zeros(nz) # kg/kg, specific humidity
ms_qi = np.zeros(nz) # kg/kg, clund ice
ms_qs = np.zeros(nz) # kg/kg, snow
ms_qg = np.zeros(nz) # kg/kg, graupel      
qv = np.zeros(nz) # kg/kg, mixing ratio of water vapour
qice = np.zeros(nz) # kg/kg, mixing ratio of ice

ave_all = np.zeros(nt)
ave_under15 = np.zeros(nt)

# 事前処理: 各ファイルを memmap
files = {var: np.memmap(f"{input_folder}ms_{var}.grd", dtype=">f4", mode="r", shape=(nt, nz, ny, nx))
         for var in ["tem", "qv", "qg"]}

def hf_t(t):
    T  = files["tem"][t].mean(axis=(1,2))
    qv = files["qv"][t].mean(axis=(1,2))
    qg = files["qg"][t].mean(axis=(1,2))

    hf = cp * T + g * vgrid + L * qv + Lv * qg
    return hf

hf_all = Parallel(n_jobs=4)(delayed(hf_t)(t) for t in range(nt))

hf_all = np.array(hf_all)
np.save(f"{out_dir}hf.npy", hf_all)
