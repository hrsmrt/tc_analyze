"""
vorticity_z の計算

計算処理を実行します。
"""

# python $WORK/tc_analyze/analysis/whole_domain/3d/calc/vorticity_z_calc.py
import datetime
import os

import numpy as np
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.vorticity import calculate_vorticity_z

# 設定とグリッドの初期化
config = AnalysisConfig()

FOLDER = config.get_domain_path("whole_domain", "3d/vorticity_z")

os.makedirs(FOLDER, exist_ok=True)

data_all_u = np.memmap(
    os.path.join(config.input_folder, "ms_u.grd"),
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_all_v = np.memmap(
    os.path.join(config.input_folder, "ms_v.grd"),
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    """指定された時刻tのz方向渦度を計算する"""
    # (config.nz, config.ny, config.nx) の配列を取得
    data_u = data_all_u[t]  # shape: (config.nz, config.ny, config.nx)
    data_v = data_all_v[t]  # shape: (config.nz, config.ny, config.nx)

    # ✅ 共通関数を使用: utils/vorticity.py
    vor = calculate_vorticity_z(data_u, data_v, config.dx, config.dy)

    np.savez(
        os.path.join(FOLDER, f"vor_t{str(t).zfill(3)}.npz"),
        data=vor,
        timestamp=datetime.datetime.now().isoformat(),
        description=f"Vorticity Z component at t={t}",
        time_step=t,
    )
    # print(f"t: {t} vorticity calc done, saved to vor_t{str(t).zfill(3)}.npz")


Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
