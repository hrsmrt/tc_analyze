# Utils物理計算関数リファレンス

## 📚 目次
1. [基礎物理定数](#基礎物理定数)
2. [熱力学計算](#熱力学計算)
3. [風速計算](#風速計算)
4. [流体力学計算](#流体力学計算)
5. [方位角平均計算](#方位角平均計算)
6. [数値計算](#数値計算)

---

## 基礎物理定数

### utils/basic.py

#### 基本物理定数（普遍定数）
- `K_B` = 1.380649e-23 J/K - ボルツマン定数
- `N_A` = 6.02214076e23 mol⁻¹ - アボガドロ数
- `R` = 8.314 J/(mol·K) - 気体定数

#### 気体定数（物理記号）
- `Rd` = 287.05 J/(kg·K) - 乾燥空気の気体定数
- `Rv` = 461 J/(kg·K) - 水蒸気の気体定数

#### 比熱（物理記号）
- `Cp` = 1004 J/(kg·K) - 乾燥空気の定圧比熱

#### 潜熱（物理記号）
- `Lv` = 2.5e6 J/kg - 水の蒸発潜熱
- `Ls` = 2.8345e6 J/kg - 水の昇華潜熱
- `Lf` = Ls - Lv - 水の融解潜熱

#### 重力・圧力
- `g` = 9.80665 m/s² - 標準重力加速度
- `PRES_S` = 1.0e5 Pa - 基準気圧 (1000 hPa)

#### 地球定数
- `ae` = 6378.137e3 m - 赤道半径
- `ap` = 6356.752e3 m - 極半径
- `G` = 6.67428e11 m³/kg/s² - 重力定数
- `G_MS` = 1.32712440041e20 m³/s² - 日心重力定数
- `G_ME` = 3.986004356e14 m³/s² - 地心重力定数

---

## 熱力学計算

### 飽和水蒸気圧

#### utils/basic.py

**tetens(T)** - Tetensの式
```python
入力: T [K] - 気温
出力: es [Pa] - 飽和水蒸気圧

特徴:
- T > 273.15 K: 水上の式 (A=7.5, B=237.3)
- T ≤ 273.15 K: 氷上の式 (A=9.5, B=265.5)
- ベクトル化対応
```

**goff_gratch(T)** - Goff-Gratchの式
```python
入力: T [K] - 気温
出力: es [Pa] - 飽和水蒸気圧

特徴:
- より高精度
- 気象学の標準式
```

### 温位

#### utils/basic.py

**potential_temperature(T, p)** - 温位計算
```python
入力:
  T [K] - 気温
  p [Pa] - 気圧
出力: θ [K] - 温位

式: θ = T(P₀/P)^(Rd/Cp)
  P₀ = 1.0e5 Pa (基準気圧)
```

### 相当温位

#### utils/thermodynamics.py

**calculate_theta_e(tem, pres, qv)** - 相当温位計算
```python
入力:
  tem [K] - 気温
  pres [Pa] - 気圧
  qv [kg/kg] - 比湿
出力: θ_e [K] - 相当温位

式: θ_e = T(Ps/P)^(Rd/Cp) * exp(Lv*rv/(Cp*T))
  rv = qv / (1 - qv)  # 混合比
```

**calculate_theta_e_from_memmap(data_tem, data_pres, data_qv, t)** - メモリマップ版
```python
メモリマップから時刻tのデータを読み込んで相当温位を計算
オンデマンド計算によりストレージを節約
```

---

## 風速計算

### utils/wind.py

#### 相対風（移動座標系）

**calculate_relative_wind(u, v, center_u, center_v)** - 相対風計算
```python
入力:
  u, v [m/s] - 絶対座標系の風速
  center_u, center_v [m/s] - 台風中心の移動速度
出力:
  u_rel, v_rel [m/s] - 相対風

式:
  u_rel = u - center_u
  v_rel = v - center_v
```

**calculate_relative_wind_from_memmap(data_u, data_v, t, center_u_list, center_v_list)**
```python
メモリマップから時刻tの相対風を計算
```

#### 動径・接線風（極座標成分）

**calculate_radial_tangential_wind(u, v, cx, cy, grid_handler)** - 極座標変換
```python
入力:
  u, v [m/s] - 直交座標系の風速
  cx, cy [m] - 台風中心座標
  grid_handler - グリッドハンドラー
出力:
  v_radial [m/s] - 動径風（中心向き正）
  v_tangential [m/s] - 接線風（反時計回り正）

式:
  θ = arctan2(y-cy, x-cx)
  v_radial = u*cos(θ) + v*sin(θ)
  v_tangential = -u*sin(θ) + v*cos(θ)
```

#### 統合計算

**calculate_relative_wind_radial_tangential(...)** - 相対風の極座標成分を一度に計算
```python
相対風計算と極座標変換を一度に実行
中間データを保存不要でストレージ大幅節約
```

**calculate_absolute_wind_radial_tangential(...)** - 絶対風の極座標成分
```python
絶対座標系での風の極座標成分を計算
```

---

## 流体力学計算

### utils/streamfunction.py

#### ポアソン方程式の解法

**poisson_periodic_fft(rhs, lx, ly)** - 2D周期境界でのポアソン方程式
```python
入力:
  rhs [ny, nx] - 右辺（渦度など）
  lx, ly [m] - ドメインサイズ
出力:
  phi [ny, nx] - 解（流線関数など）

式: ∇²φ = rhs
```

#### 流線関数

**calculate_streamfunction(zeta, dx, dy)** - 渦度から流線関数を計算
```python
入力:
  zeta [ny, nx] or [nz, ny, nx] - 渦度場
  dx, dy [m] - 格子間隔
出力:
  psi - 流線関数

式: ∇²ψ = -ζ
```

**calculate_streamfunction_from_memmap(data_vorticity_z, t, dx, dy)**
```python
メモリマップから時刻tの流線関数を計算
```

#### FFTサブピクセルシフト

**frac_roll_x_fft(row, shift)** - 実数シフト
```python
1次元配列を周期境界でサブピクセル精度でシフト
FFTを用いた位相シフト
```

---

## 方位角平均計算

### utils/azimuthal.py

#### 基本的な方位角平均

**calculate_azimuthal_mean_3d(data, t, center_x_list, center_y_list, grid_handler, r_max)**
```python
入力:
  data [nt, nz, ny, nx] - 3Dデータ
  t - 時刻インデックス
  center_x_list, center_y_list [m] - 台風中心座標リスト
  grid_handler - グリッドハンドラー
  r_max [m] - 最大半径（デフォルト: 1000km）
出力:
  azim_mean [nz, nr] - 方位角平均データ

物理的意味:
  台風中心からの距離rごとに、方位角方向に平均
  軸対称を仮定した解析に使用
```

**calculate_azimuthal_mean_2d(...)** - 2Dデータ版
```python
地表面データなどの2次元データの方位角平均
出力: [nr]
```

#### 風速の方位角平均

**calculate_azimuthal_mean_wind(data_u, data_v, t, ...)** - 絶対風の極座標成分
```python
出力:
  azim_radial [nz, nr] - 動径風の方位角平均
  azim_tangential [nz, nr] - 接線風の方位角平均

物理的意味:
  台風の軸対称構造を抽出
  動径流入・接線循環の解析
```

**calculate_azimuthal_mean_relative_wind(...)** - 相対風の極座標成分
```python
台風の移動を考慮した相対風の方位角平均
移動座標系での軸対称構造の解析
```

**calculate_azimuthal_mean_wind10m(data_u10, data_v10, t, ...)** - 10m風
```python
地上10m高度の風の方位角平均
```

#### 熱力学変数の方位角平均

**calculate_azimuthal_mean_theta(data_tem, data_pres, t, ...)** - 温位
```python
出力: azim_theta [nz, nr] - 温位の方位角平均 [K]

物理的意味:
  台風の熱的構造を表現
  温位の動径分布から成層状態を診断
```

**calculate_azimuthal_mean_theta_e(data_tem, data_pres, data_qv, t, ...)** - 相当温位
```python
出力: azim_theta_e [nz, nr] - 相当温位の方位角平均 [K]

物理的意味:
  潜熱を含む全エネルギーを表現
  対流不安定の診断に使用
```

#### 運動量フラックス

**calculate_azimuthal_mean_momentum(azim_tangential, config, r_max)** - 角運動量
```python
入力: azim_tangential [nz, nr] - 接線風の方位角平均
出力: azim_momentum [nz, nr] - 角運動量の方位角平均

式: M = (r + r₀) * v
  r₀ = f * r² / (2 * v)  # 慣性半径相当
```

---

## 数値計算

### utils/basic.py

#### 時間微分

**central_difference_2nd(data, dt)** - 2次精度中心差分
```python
入力:
  data [nt, ...] - 時系列データ
  dt [s] - 時間間隔
出力:
  derivative [nt, ...] - 時間微分

手法:
  内点: (data[i+1] - data[i-1]) / (2*dt)  # 2次精度
  始点: (data[1] - data[0]) / dt         # 前進差分
  終点: (data[-1] - data[-2]) / dt       # 後退差分
```

**calculate_center_velocity(center_x, center_y, dt)** - 台風中心移動速度
```python
入力:
  center_x, center_y [m] - 台風中心座標の時系列
  dt [s] - 時間間隔
出力:
  center_u, center_v [m/s] - 移動速度

物理的意味:
  台風の移動速度を計算
  相対風の計算に使用
```

---

## 使用例

### 1. 温位の計算と方位角平均

```python
from utils.basic import potential_temperature
from utils.azimuthal import calculate_azimuthal_mean_theta

# 温位を直接計算
theta = potential_temperature(T, p)

# または、方位角平均を一度に計算
azim_theta = calculate_azimuthal_mean_theta(
    data_tem, data_pres, t,
    center_x_list, center_y_list,
    grid_handler
)
```

### 2. 相対風の動径・接線成分

```python
from utils.basic import calculate_center_velocity
from utils.wind import calculate_relative_wind_radial_tangential

# 台風中心の移動速度を計算
center_u_list, center_v_list = calculate_center_velocity(
    center_x_list, center_y_list, dt
)

# 相対風の極座標成分を計算
v_radial, v_tangential = calculate_relative_wind_radial_tangential(
    data_u, data_v, t,
    center_x_list, center_y_list,
    center_u_list, center_v_list,
    grid_handler
)
```

### 3. 流線関数の計算

```python
from utils.streamfunction import calculate_streamfunction

# 渦度から流線関数を計算
psi = calculate_streamfunction(zeta, dx, dy)
```

---

## 設計思想

### オンデマンド計算
- 中間データを保存せず、必要時に計算
- ストレージを数GB〜数百GB節約
- `_from_memmap` 関数でメモリマップから直接計算

### 一元化された物理定数
- `basic.py` に全ての基礎定数を集約
- 計算式の変更が1箇所で済む
- 精度の統一が保証される

### 関数の合成
- 小さな関数を組み合わせて複雑な計算を実現
- 例: `calculate_azimuthal_mean_theta` = 方位角平均 + 温位計算
- コードの再利用性が高い

---

## 物理的意味の理解

### 台風解析の文脈

1. **軸対称成分の抽出** (方位角平均)
   - 台風の基本構造を理解
   - 非軸対称成分との分離

2. **移動座標系** (相対風)
   - 台風に追随した座標系
   - 台風内部の循環を正しく評価

3. **極座標成分** (動径・接線風)
   - 動径風: 流入・流出を表現
   - 接線風: 旋回を表現
   - 台風の力学を理解する基本

4. **熱力学的構造** (温位・相当温位)
   - 温位: 成層安定度
   - 相当温位: 対流不安定性
   - エネルギー保存則の理解

---

## 関数一覧（アルファベット順）

### basic.py
- `calculate_center_velocity()` - 台風中心移動速度
- `central_difference_2nd()` - 2次精度中心差分
- `goff_gratch()` - 飽和水蒸気圧（Goff-Gratch式）
- `potential_temperature()` - 温位
- `tetens()` - 飽和水蒸気圧（Tetens式）

### thermodynamics.py
- `calculate_theta_e()` - 相当温位
- `calculate_theta_e_from_memmap()` - 相当温位（メモリマップ版）

### wind.py
- `calculate_absolute_wind_radial_tangential()` - 絶対風の極座標成分
- `calculate_radial_tangential_wind()` - 極座標変換
- `calculate_relative_wind()` - 相対風
- `calculate_relative_wind_from_memmap()` - 相対風（メモリマップ版）
- `calculate_relative_wind_radial_tangential()` - 相対風の極座標成分

### streamfunction.py
- `calculate_streamfunction()` - 流線関数
- `calculate_streamfunction_from_memmap()` - 流線関数（メモリマップ版）
- `frac_roll_x_fft()` - FFTサブピクセルシフト
- `poisson_periodic_fft()` - ポアソン方程式の解法

### azimuthal.py
- `calculate_azimuthal_mean_2d()` - 2Dデータの方位角平均
- `calculate_azimuthal_mean_3d()` - 3Dデータの方位角平均
- `calculate_azimuthal_mean_momentum()` - 角運動量の方位角平均
- `calculate_azimuthal_mean_relative_wind()` - 相対風の方位角平均
- `calculate_azimuthal_mean_theta()` - 温位の方位角平均
- `calculate_azimuthal_mean_theta_e()` - 相当温位の方位角平均
- `calculate_azimuthal_mean_wind()` - 風速の方位角平均
- `calculate_azimuthal_mean_wind10m()` - 10m風の方位角平均

---

**作成日**: 2025-11-27
**最終更新**: 2025-11-27
**バージョン**: 1.0
