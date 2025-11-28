"""
cape

解析処理を実行します。
"""

# nohup python $WORK/tc_analyze/cape.py &

# CAPEの計算
# 参考: Holton演習、Satoh(2014)p403
# モデル最下層(z=33m)のパーセルを考える
# LCL(lifting condensation level)まで: 乾燥断熱減率
# LCL〜LFC(level of free convection)〜ZT(浮力が0になる高度)まで: 湿潤断熱減率

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from joblib import Parallel, delayed

from utils.basic import Cp, Lv, Rd, Rv, g, tetens
from utils.config import AnalysisConfig
from utils.plotting import parse_style_argument

# スタイルシートの解析
mpl_style_sheet = parse_style_argument()

# 設定とグリッドの初期化
config = AnalysisConfig()

vgrid = np.loadtxt(config.vgrid_filepath)

OUT_DIR = config.get_fig_path("cape")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "parcel_T"), exist_ok=True)
os.makedirs(os.path.join(OUT_DIR, "parcel_rho"), exist_ok=True)

# I/O最適化: memmapを使用
ms_tem_memmap = np.memmap(
    f"{config.input_folder}ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
ms_pres_memmap = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
ms_rho_memmap = np.memmap(
    f"{config.input_folder}ms_rho.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
ms_rh_memmap = np.memmap(
    f"{config.input_folder}ms_rh.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)


def process_t(t):
    """時刻tのCAPE計算とプロット生成を行い、CAPE値を返す"""
    # データの読み込みと平均
    T_env = ms_tem_memmap[t].mean(axis=(1, 2))  # (nz,)
    p_env = ms_pres_memmap[t].mean(axis=(1, 2))  # (nz,)
    ms_rho = ms_rho_memmap[t].mean(axis=(1, 2))  # (nz,)
    rh_env = ms_rh_memmap[t].mean(axis=(1, 2))  # (nz,)

    # パーセル温度の計算
    T = calc_T(t, T_env[0], p_env, rh_env[0])
    rho_env = p_env / Rd / T_env
    rho = p_env / Rd / T

    # CAPE計算
    lfc = False
    cape = 0
    for z in range(1, config.nz):
        b = (
            (rho[z] + rho[z - 1] - rho_env[z] - rho_env[z - 1])
            / (rho_env[z] + rho_env[z - 1])
            * g
        )
        if lfc == False and rho[z] < rho_env[z]:
            lfc = True
        if lfc and rho[z] > rho_env[z]:
            break
        cape -= b * (vgrid[z] - vgrid[z - 1])

    # Temperature plot
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(T_env, vgrid * 1e-3, label="Environment")
    ax.plot(T, vgrid * 1e-3, label="Percel")
    ax.set_ylabel("z [km]")
    ax.set_xlabel("Temperature [K]")
    ax.set_title(f"t={config.time_list[t]} hour, CAPE={cape:.1f} J/kg")
    ax.grid()
    ax.legend()
    fig.savefig(os.path.join(OUT_DIR, f"parcel_T/t{config.time_list[t]:04d}h.png"))
    plt.close()

    # Density plot
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(rho_env - ms_rho, vgrid * 1e-3, label="Environment(rho_env-ms_rho)")
    ax.plot(rho - ms_rho, vgrid * 1e-3, label="Percel-ms_rho")
    ax.set_ylabel("z [km]")
    ax.set_xlabel("Density [kg/m^3]")
    ax.set_title(f"t={config.time_list[t]} hour")
    ax.grid()
    ax.legend()
    fig.savefig(os.path.join(OUT_DIR, f"parcel_rho/t{config.time_list[t]:04d}h.png"))
    plt.close()

    return t, cape


def main():
    """並列処理でCAPE計算を実行"""
    # 並列処理で各時刻のCAPEを計算
    results = Parallel(n_jobs=config.n_jobs)(
        delayed(process_t)(t)
        for t in range(config.t_first, config.t_last + 1, config.t_step)
    )

    # 結果を集約（時刻順にソート）
    results.sort(key=lambda x: x[0])
    cape_evol = np.zeros(config.nt)
    for t, cape in results:
        cape_evol[t] = cape
        print(f"t={config.time_list[t]:3d}h: CAPE={cape:.1f} J/kg")

    # CAPE時系列プロット
    plt.style.use(mpl_style_sheet)
    fig, ax = plt.subplots(figsize=(10, 6))
    time_values = [config.time_list[t] for t, _ in results]
    cape_values = [cape for _, cape in results]
    ax.plot(time_values, cape_values, 'o-', linewidth=2, markersize=6)
    ax.set_ylim([0, 5000])
    ax.set_title("CAPE Evolution", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time [hour]", fontsize=12)
    ax.set_ylabel("CAPE [J/kg]", fontsize=12)
    ax.grid(True, alpha=0.3)
    fig.savefig(os.path.join(OUT_DIR, "cape.png"), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n✅ 完了: {OUT_DIR}")


def calc_T(t, T_zb, p_env, rh_zb):
    # パーセル
    T = np.zeros(config.nz)  # K, 気温
    pd = np.zeros(config.nz)  # Pa 乾燥空気の圧力
    e = np.zeros(config.nz)  # Pa 水蒸気の圧力
    es = np.zeros(config.nz)  # Pa 飽和水蒸気圧
    T[0] = T_zb
    es[0] = tetens(T[0])
    e[0] = rh_zb * es[0]
    pd[0] = p_env[0] - e[0]
    e_par_p = e[0] / p_env[0]

    houwa = False
    for i in range(1, config.nz):
        alpha = Rv * T[i - 1] / p_env[i - 1]
        if houwa == False:  # 飽和するまで
            T[i] = T[i - 1] + alpha / Cp * (p_env[i] - p_env[i - 1])
            e[i] = e_par_p * p_env[i]
            es[i] = es[i - 1] + Lv / (Rv * T[i] ** 2) * es[i - 1] * (T[i] - T[i - 1])
            if e[i] > es[i]:
                houwa = True
                print(
                    f"{
                        config.time_list[t]}h, 高度{
                        vgrid[i] /
                        1000}kmで飽和(e={
                        e[i] /
                        100:.2f}hPa,es={
                        es[i] /
                        100:.2f}hPa)",
                    end="",
                )
        else:  # 飽和したのち
            # 計算に必要な量を求める
            pd = p_env[i - 1] - es[i - 1]
            rho = pd / (Rd * T[i - 1])
            alpha = 1 / rho
            A = (
                Lv
                * es[i - 1]
                / (Cp * rho * Rv * T[i - 1] ** 2)
                * (Lv / (Rv * T[i - 1]) - 1)
            )

            # 次の高度の温度、圧力を求める
            T[i] = T[i - 1] + 1 / (1 + A) * alpha / Cp * (p_env[i] - p_env[i - 1])
            es[i] = es[i - 1] + Lv / (Rv * T[i] ** 2) * es[i - 1] * (T[i] - T[i - 1])
            e[i] = es[i]
    return T


if __name__ == "__main__":
    main()
