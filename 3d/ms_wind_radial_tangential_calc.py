# python $WORK/tc_analyze/3d/ms_wind_radial_tangential_calc.py
"""
風速の放射状・接線方向成分を計算

直交座標系の風速(u, v)を、台風中心からの放射状成分と接線方向成分に変換します。
"""
import os
import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

# 出力フォルダの作成
folder1 = "./data/3d/wind_radial/"
folder2 = "./data/3d/wind_tangential/"
os.makedirs(folder1, exist_ok=True)
os.makedirs(folder2, exist_ok=True)

# 中心座標の読み込み
center_x_list = config.center_x
center_y_list = config.center_y

# データのメモリマップ
data_all_u = np.memmap(
    f"{config.input_folder}/ms_u.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx)
)
data_all_v = np.memmap(
    f"{config.input_folder}/ms_v.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx)
)

def process_t(t):
    """
    時刻tにおける放射状・接線方向成分を計算

    Args:
        t (int): 時刻ステップ
    """
    # 中心座標（m単位）
    cx = center_x_list[t]
    cy = center_y_list[t]

    # データ取得 (config.nz, config.ny, config.nx)
    data_u = data_all_u[t]
    data_v = data_all_v[t]

    # 直交座標系から極座標系への変換
    v_radial, v_tangential = grid.uv_to_radial_tangential(data_u, data_v, cx, cy)

    # 結果を保存
    np.save(f"{folder1}/t{str(t).zfill(3)}.npy", v_radial)
    np.save(f"{folder2}/t{str(t).zfill(3)}.npy", v_tangential)

    print(f"t: {t} done")

# 並列処理で全時刻を処理
Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_first, config.t_last))
