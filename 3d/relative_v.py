"""
relative_v

解析処理を実行します。
"""

# python $WORK/tc_analyze/3d/relative_v.py
import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

os.makedirs(str(f"./data/3d/relative_v"),exist_ok=True)

x_axis = np.arange(0.5*config.dx,config.nx*config.dx,config.dx) * 1e-3
y_axis = np.arange(0.5*config.dy,config.ny*config.dy,config.dy) * 1e-3
grid.X, grid.Y = np.meshgrid(x_axis,y_axis)

center_y_list = config.center_y

center_v_list = np.zeros(len(center_y_list))
center_v_list[1:-1] = (center_y_list[2:] - center_y_list[:-2]) / (2 * config.dt_output)
center_v_list[0] = (center_y_list[1] - center_y_list[0]) / (config.dt_output)
center_v_list[-1] = (center_y_list[-1] - center_y_list[-2]) / (config.dt_output)

data_memmap = np.memmap(f"{config.input_folder}ms_v.grd",dtype=">f4",mode="r",shape=(config.nt,config.nz,config.ny,config.nx))

def process_t(t):
    data = data_memmap[t,:,:,:]
    data_rel = data - center_v_list[t]
    np.save(f"./data/3d/relative_v/t{str(t).zfill(3)}.npy",data_rel)
    print(f"Saved: ./data/3d/relative_v/t{str(t).zfill(3)}.npy")

Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
