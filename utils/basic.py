import numpy as np

# 基礎定数
k_boltzmann = 1.380649e-23 # ボルツマン定数 [J/K], 理科年表2022
Na = 6.02214076e23 # アボガドロ数 [mol^-1], 理科年表2022
R = k_boltzmann * Na # 気体定数 [J/(mol K)], 理科年表2022
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


ae = 6378.137e3 # m. 赤道半径　# 天文(理科年表2022)
ap = 6356.752e3 # m. 極半径　# 天文(理科年表2022)
G = 6.67428e11 # m3/kg/s2. 重力定数　# 天文(理科年表2022)
GMs = 1.32712440041e20 # m3/s2. 日心重力定数　# 天文(理科年表2022)
GMe = 3.986004356e14 # m3/s2. 地心重力定数　# 天文(理科年表2022)

g0 = 9.80665 # m/s2. Holton and Hakim(2014)p19

Cp_dry = 1004 # J/(kg K). 乾燥空気の定圧比熱

DryAir_weight = 0.78*N2_weight + 0.21*O2_weight + 9.3e-3*Ar_weight + 3.9e-4*CO2_weight + 1.8e-5*Ne_weight + 5.2e-6*He_weight
Rd = R / DryAir_weight * 1e3 # 乾燥空気の気体定数 [J/(kg K)]
Rv = R / H2O_weight * 1e3 # 水蒸気の気体定数 [J/(kg K)]

# Tetensの式, Satoh(2013) p256
def tetens(T):
  if (T > 273.15):
    A = 7.5
    B = 237.3
  else:
    A = 9.5
    B = 265.5
  T0 = 273.15
  p0 = 6.1078e2 # Pa
  T_ = T - T0
  es = p0 * np.power(10,A * T_/ (B + T_))
  return es
# Goff-Gratch formula, Satoh(2013) p256
def goff_gratch(T): # おそらく、氷点下以下に対しては係数を変える必要がある
  Ts = 373.16
  t = T/Ts
  ps = 101324.6 # Pa
  a = -7.90298*(1/t-1)-5.02808*np.log10(t) \
      -1.3816e-7*(np.power(10,11.344*(1-t))-1) \
      +8.1328e-3*(np.power(10,-3.19149*(1/t-1))-1)
  es = ps * np.power(10,a)
  return es

def potential_temperature(T, p):
  p0 = 1e5 # Pa
  kappa = Rd / Cp_dry
  theta = T * (p0 / p)**kappa
  return theta

if __name__ == "__main__":
    print(k_boltzmann,"ボルツマン定数 [J/K]")
    print(Na,"アボガドロ数 [mol^-1]")
    print(R,"気体定数 [J/(mol K)]")
    print(f"地表の重力加速度:{g0} m/s2")
    print("乾燥大気の平均分子量 [u]",DryAir_weight) # 乾燥大気の平均分子量 [u]
    print("乾燥空気の気体定数 [J/(kg K)]",Rd)
    print("水蒸気の気体定数 [J/(kg K)]",Rv)
