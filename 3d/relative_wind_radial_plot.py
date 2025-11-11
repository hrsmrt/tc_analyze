# python $WORK/tc_analyze/3d/relative_wind_radial_plot.py $style
"""
相対風の放射状成分をプロット

指定された鉛直レベルにおける放射状風速成分の水平分布をプロットします。
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument

# 設定とグリッドの初期化
config = AnalysisConfig()
grid = GridHandler(config)

# スタイルシートの解析と適用
mpl_style_sheet = parse_style_argument()

# 出力フォルダの作成
os.makedirs("./fig/3d/vortex_region/relative_wind_radial/", exist_ok=True)

# 描画設定
radial_max = 500e3
extent_x = int(radial_max / config.dx)
extent_y = int(radial_max / config.dy)

# 中心座標と鉛直グリッドの読み込み
center_x_list = config.center_x
center_y_list = config.center_y
vgrid = np.loadtxt(config.vgrid_filepath)

# 切り出し領域のメッシュグリッド
X_cut = grid.X[: extent_y * 2, : extent_x * 2]
Y_cut = grid.Y[: extent_y * 2, : extent_x * 2]

# 距離を計算（円形マスク用）
R = np.sqrt((radial_max - X_cut)**2 + (radial_max - Y_cut)**2)

# 鉛直レベルリスト
z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(f"./fig/3d/vortex_region/relative_wind_radial/z{str(z).zfill(2)}", exist_ok=True)

def process_t(t):
    """
    時刻tにおける放射状風速成分をプロット

    Args:
        t (int): 時刻ステップ
    """
    data_t = np.load(f"./data/3d/relative_wind_radial/t{str(t).zfill(3)}.npy")

    # 中心座標をインデックスに変換
    center_x = int(center_x_list[t] / config.dx)
    center_y = int(center_y_list[t] / config.dy)

    # 周期境界条件を考慮したインデックス
    x_idx = [(center_x - extent_x + i) % config.nx for i in range(2 * extent_x)]
    y_idx = [(center_y - extent_y + i) % config.ny for i in range(2 * extent_y)]

    for z in z_list:
        data = data_t[z, :, :]
        data_cut = data[np.ix_(y_idx, x_idx)]

        # 半径制限を超える部分をマスク
        data_masked = np.ma.masked_where(R > radial_max, data_cut)

        # プロット作成
        if mpl_style_sheet:
            plt.style.use(mpl_style_sheet)

        fig, ax = plt.subplots(figsize=(3, 2.5))
        cf = ax.contourf(
            X_cut, Y_cut, data_masked,
            cmap="bwr",
            levels=np.arange(-30, 35, 5),
            extend='both'
        )
        fig.colorbar(cf, ax=ax)

        # 軸の設定
        ax.set_xticks(
            [0, extent_x * config.dx, 2 * extent_x * config.dx],
            [int(-extent_x * config.dx * 1e-3), "0", int(extent_x * config.dx * 1e-3)],
        )
        ax.set_yticks(
            [0, extent_y * config.dy, 2 * extent_y * config.dy],
            [int(-extent_y * config.dy * 1e-3), "0", int(extent_y * config.dy * 1e-3)],
        )

        # タイトルとラベル
        ax.set_title(f"t={t}h, z={round(vgrid[z]*1e-3, 1):.1f}km")
        ax.set_xlabel("x [km]")
        ax.set_ylabel("y [km]")
        ax.set_aspect("equal", "box")

        # 保存
        fig.savefig(
            f"./fig/3d/vortex_region/relative_wind_radial/z{str(z).zfill(2)}/t{str(config.time_list[t]).zfill(3)}.png"
        )
        plt.close()

# 並列処理で全時刻を処理（24時間ごと）
Parallel(n_jobs=config.n_jobs)(delayed(process_t)(t) for t in range(config.t_start, config.t_end, int(24 / config.dt_hour)))
