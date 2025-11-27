"""
熱力学的変数の計算関数

データを保存せず、必要時にその場で計算する関数を提供します。
ストレージを大幅に節約できます。
"""

import numpy as np

from .basic import PRES_S, Rd, Cp, Lv

# 事前計算
Rd_Cp = Rd / Cp


def calculate_theta_e(tem, pres, qv):
    """
    相当温位 θ_e を計算

    θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))

    Parameters
    ----------
    tem : ndarray
        気温 [K]
    pres : ndarray
        気圧 [Pa]
    qv : ndarray
        比湿 [kg/kg]

    Returns
    -------
    theta_e : ndarray
        相当温位 [K]

    Notes
    -----
    - データを保存せず、必要時に計算
    - ストレージ節約のため
    """
    # 混合比 rv = qv / (1 - qv)
    rv = qv / (1.0 - qv)

    # θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))
    theta_e = tem * (PRES_S / pres) ** Rd_Cp * np.exp(Lv * rv / (Cp * tem))

    return theta_e.astype(np.float32)


def calculate_theta_e_from_memmap(data_tem, data_pres, data_qv, t):
    """
    メモリマップから相当温位を計算

    Parameters
    ----------
    data_tem : memmap
        気温データのメモリマップ
    data_pres : memmap
        気圧データのメモリマップ
    data_qv : memmap
        比湿データのメモリマップ
    t : int
        時刻インデックス

    Returns
    -------
    theta_e : ndarray
        相当温位 [K]
    """
    tem = data_tem[t]
    pres = data_pres[t]
    qv = data_qv[t]

    return calculate_theta_e(tem, pres, qv)
