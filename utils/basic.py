"""Basic physical constants and utility functions for atmospheric calculations."""

import numpy as np

# 基本物理定数（普遍定数）
K_B = 1.380649e-23  # ボルツマン定数 [J/K], 理科年表2022
N_A = 6.02214076e23  # アボガドロ数 [mol^-1], 理科年表2022
R = K_B * N_A  # 気体定数 [J/(mol·K)], 理科年表2022
H_weight = 0.5*(1.00784 + 1.00811) # 水素の原子量 [u], 原子量表(2024)
He_weight = 4.002602 # ヘリウムの原子量 [u], 原子量表(2024) # 原子量は、同位体元素の平均値
Ne_weight = 20.1797 # ネオンの原子量 [u], 原子量表(2024)
Ar_weight  = 0.5*(39.792+39.963) # アルゴンの原子量 [u], 原子量表(2024)
N_weight = 0.5*(14.00643+14.00728)
O_weight = 0.5*(15.99903+15.99977)
C_weight = 0.5*(15.99903+15.99977)
N2_weight = 2.0*N_weight
O2_weight = 2.0*O_weight
CO_weight = C_weight + O_weight
CO2_weight = C_weight + O_weight * 2
H2O_weight = 2*H_weight + O_weight


ae = 6378.137e3  # m. 赤道半径　# 天文(理科年表2022)
ap = 6356.752e3  # m. 極半径　# 天文(理科年表2022)
G = 6.67428e11  # m³/kg/s². 重力定数　# 天文(理科年表2022)
G_MS = 1.32712440041e20  # m³/s². 日心重力定数　# 天文(理科年表2022)
G_ME = 3.986004356e14  # m³/s². 地心重力定数　# 天文(理科年表2022)

g = 9.80665  # m/s². 標準重力加速度, Holton and Hakim(2014)p19

# 比熱（物理記号）
Cp = 1004  # J/(kg·K). 乾燥空気の定圧比熱

# 気体定数（物理記号）
DryAir_weight = (0.78 * N2_weight + 0.21 * O2_weight + 9.3e-3 * Ar_weight
                 + 3.9e-4 * CO2_weight + 1.8e-5 * Ne_weight
                 + 5.2e-6 * He_weight)
Rd = R / DryAir_weight * 1e3  # 乾燥空気の気体定数 [J/(kg·K)]
Rv = R / H2O_weight * 1e3  # 水蒸気の気体定数 [J/(kg·K)]

# 潜熱（物理記号）
Lv = 2.5e6  # 水の蒸発潜熱 [J/kg]
Ls = 2.8345e6  # 水の昇華潜熱 [J/kg]
Lf = Ls - Lv  # 水の融解潜熱 [J/kg]

# 基準気圧
PRES_S = 1.0e5  # 基準気圧 [Pa] (= 1000 hPa)

# Tetensの式, Satoh(2013) p256
def tetens(T):
    """
    Calculate saturation vapor pressure using Tetens formula.

    Parameters
    ----------
    T : float or ndarray
        Temperature [K]

    Returns
    -------
    es : float or ndarray
        Saturation vapor pressure [Pa]
    """
    # ベクトル化対応: スカラーと配列の両方に対応
    T = np.asarray(T)
    scalar_input = T.ndim == 0
    T = np.atleast_1d(T)

    # 水上（T > 273.15）と氷上（T <= 273.15）で係数を切り替え
    A = np.where(T > 273.15, 7.5, 9.5)
    B = np.where(T > 273.15, 237.3, 265.5)

    T0 = 273.15
    p0 = 6.1078e2  # Pa
    T_ = T - T0
    es = p0 * np.power(10, A * T_ / (B + T_))

    if scalar_input:
        return es.item()
    return es
# Goff-Gratch formula, Satoh(2013) p256
def goff_gratch(T):
    """
    Calculate saturation vapor pressure using Goff-Gratch formula.

    Note: Coefficients may need to be adjusted for temperatures below freezing.

    Parameters
    ----------
    T : float or ndarray
        Temperature [K]

    Returns
    -------
    es : float or ndarray
        Saturation vapor pressure [Pa]
    """
    Ts = 373.16
    t = T / Ts
    ps = 101324.6  # Pa
    a = (-7.90298 * (1 / t - 1) - 5.02808 * np.log10(t)
         - 1.3816e-7 * (np.power(10, 11.344 * (1 - t)) - 1)
         + 8.1328e-3 * (np.power(10, -3.19149 * (1 / t - 1)) - 1))
    es = ps * np.power(10, a)
    return es

def potential_temperature(T, p):
    """
    Calculate potential temperature.

    Parameters
    ----------
    T : float or ndarray
        Temperature [K]
    p : float or ndarray
        Pressure [Pa]

    Returns
    -------
    theta : float or ndarray
        Potential temperature [K]
    """
    p0 = 1e5  # Pa
    kappa = Rd / Cp
    theta = T * (p0 / p)**kappa
    return theta


# ========================================
# 数値微分
# ========================================

def central_difference_2nd(data, dt):
    """
    2次精度の中心差分による時間微分を計算

    d/dt ≈ (data[i+1] - data[i-1]) / (2*dt)  (内点)

    Parameters
    ----------
    data : ndarray (nt,) or (nt, ...)
        時系列データ（1次元目が時間）
    dt : float
        時間間隔

    Returns
    -------
    derivative : ndarray
        時間微分（dataと同じ形状）

    Notes
    -----
    - 内点: 2次精度中心差分
    - 始点: 前進差分 (data[1] - data[0]) / dt
    - 終点: 後退差分 (data[-1] - data[-2]) / dt

    Examples
    --------
    >>> x = np.array([0, 1, 4, 9, 16])  # t^2
    >>> v = central_difference_2nd(x, dt=1.0)  # d/dt(t^2) = 2t
    >>> print(v)  # [1, 2, 4, 6, 7] (理論値: [0, 2, 4, 6, 8])
    """
    data = np.asarray(data)
    nt = data.shape[0]
    derivative = np.zeros_like(data, dtype=np.float32)

    # 内点: 2次精度中心差分
    derivative[1:-1] = (data[2:] - data[:-2]) / (2.0 * dt)

    # 始点: 前進差分
    derivative[0] = (data[1] - data[0]) / dt

    # 終点: 後退差分
    derivative[-1] = (data[-1] - data[-2]) / dt

    return derivative


def calculate_center_velocity(center_x, center_y, dt):
    """
    台風中心の移動速度を2次中心差分で計算

    Parameters
    ----------
    center_x : ndarray (nt,)
        台風中心のx座標 [m]
    center_y : ndarray (nt,)
        台風中心のy座標 [m]
    dt : float
        時間間隔 [s]

    Returns
    -------
    center_u : ndarray (nt,)
        x方向移動速度 [m/s]
    center_v : ndarray (nt,)
        y方向移動速度 [m/s]

    Notes
    -----
    - 内点: 2次精度中心差分 u[i] = (x[i+1] - x[i-1]) / (2*dt)
    - 端点: 前進/後退差分

    Examples
    --------
    >>> cx = np.array([0, 100, 250, 450])  # [m]
    >>> cy = np.array([0, 80, 180, 300])   # [m]
    >>> u, v = calculate_center_velocity(cx, cy, dt=3600)  # 1時間
    >>> print(u)  # x方向移動速度 [m/s]
    """
    center_u = central_difference_2nd(center_x, dt)
    center_v = central_difference_2nd(center_y, dt)

    return center_u, center_v

if __name__ == "__main__":
    print(k_boltzmann,"ボルツマン定数 [J/K]")
    print(Na,"アボガドロ数 [mol^-1]")
    print(R,"気体定数 [J/(mol K)]")
    print(f"地表の重力加速度:{g0} m/s2")
    print("乾燥大気の平均分子量 [u]",DryAir_weight) # 乾燥大気の平均分子量 [u]
    print("乾燥空気の気体定数 [J/(kg K)]",Rd)
    print("水蒸気の気体定数 [J/(kg K)]",Rv)
