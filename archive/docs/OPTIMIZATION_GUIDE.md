# 高速化ガイド（並列化以外）

**作成日**: 2025-11-25
**対象**: tc_analyzeプロジェクト

---

## 📊 ボトルネック分析結果

コードベースを分析した結果、以下の主要なボトルネックが特定されました：

### 1. **Pythonループによる配列操作**（最重要）
**影響度**: 🔴🔴🔴🔴🔴 非常に大

**問題箇所**: `azim_mean/azim_wind_calc.py` (76-77行, 88-89行)
```python
# 現在の実装（遅い）
azim_sum_radial = np.zeros((config.nz, max_bin))
for i, b in enumerate(bin_idx):
    azim_sum_radial[:, b] += v_radial[:, i]
```

**問題点**:
- Pythonループで配列の各要素にアクセス
- 100万要素のループで数秒～数十秒かかる
- NumPyのベクトル化の恩恵を受けられない

**期待される高速化**: **10-100倍**

---

### 2. **Z方向のループ**
**影響度**: 🔴🔴🔴 大

**問題箇所**: `3d/divergence_calc.py` (43-62行)
```python
# 現在の実装
for z in range(config.nz):  # 74回ループ
    du_dx = (np.roll(data_u[z], -1, axis=1) - ...) / (2 * config.dx)
    dv_dy = (np.roll(data_v[z], -1, axis=0) - ...) / (2 * config.dy)
    div[z] = du_dx + dv_dy
```

**問題点**:
- 74回のループで同じ操作を繰り返す
- メモリアクセスパターンが非効率

**期待される高速化**: **5-10倍**

---

### 3. **ファイルI/Oの繰り返し**
**影響度**: 🔴🔴 中

**問題箇所**: `azim_mean/azim_2d_calc.py` (48-51行)
```python
# 各タイムステップでファイルを開閉
with open(f"{config.input_folder}{varname}.grd", "rb") as f:
    f.seek(offset)
    data = np.fromfile(f, dtype=">f4", count=count_2d)
```

**問題点**:
- ファイルの開閉オーバーヘッド
- OSレベルのファイルキャッシュが効きにくい

**期待される高速化**: **2-3倍**

---

### 4. **重複計算**
**影響度**: 🔴 小～中

**問題箇所**: 複数のファイル
```python
# 毎回計算している
R = np.sqrt(dX**2 + dY**2)
theta = np.arctan2(dY, dX)
```

**問題点**:
- 同じ計算を複数のスクリプトで繰り返し実行
- キャッシュ可能な値を毎回計算

**期待される高速化**: **1.5-2倍**

---

## 🚀 最適化手法

### 1. ループのベクトル化（最優先）

#### 1.1 `np.add.at()`の使用

**対象**: `azim_mean/azim_wind_calc.py`

```python
# ❌ 遅い実装（現在）
azim_sum_radial = np.zeros((config.nz, max_bin))
for i, b in enumerate(bin_idx):
    azim_sum_radial[:, b] += v_radial[:, i]

# ✅ 高速化版
azim_sum_radial = np.zeros((config.nz, max_bin))
np.add.at(azim_sum_radial.T, bin_idx, v_radial.T)
# または
for z in range(config.nz):
    np.add.at(azim_sum_radial[z], bin_idx, v_radial[z])
```

**効果**: **10-100倍高速化**

#### 1.2 `np.bincount()`の活用

```python
# ❌ 遅い実装
azim_sum = np.zeros(max_bin)
for i, b in enumerate(bin_idx):
    azim_sum[b] += data[i]

# ✅ 高速化版
azim_sum = np.bincount(bin_idx, weights=data, minlength=max_bin)
```

**効果**: **50-100倍高速化**

---

### 2. 3次元配列のベクトル化

#### 2.1 Divergence計算の最適化

**対象**: `3d/divergence_calc.py`

```python
# ❌ 遅い実装（現在）
for z in range(config.nz):
    du_dx = (np.roll(data_u[z], -1, axis=1) - np.roll(data_u[z], 1, axis=1)) / (2 * config.dx)
    dv_dy = (np.roll(data_v[z], -1, axis=0) - np.roll(data_v[z], 1, axis=0)) / (2 * config.dy)
    div[z] = du_dx + dv_dy

# ✅ 高速化版
# 全z方向を一度に処理
du_dx = (np.roll(data_u, -1, axis=2) - np.roll(data_u, 1, axis=2)) / (2 * config.dx)
dv_dy = (np.roll(data_v, -1, axis=1) - np.roll(data_v, 1, axis=1)) / (2 * config.dy)

# 境界条件の処理
# 北極と南極の特殊処理（ベクトル化可能）
dv_dy[:, 0, :config.nx//2] = (data_v[:, 1, :config.nx//2] - data_v[:, -1, config.nx//2:]) / (2 * config.dy)
dv_dy[:, 0, config.nx//2:] = (data_v[:, 1, config.nx//2:] - data_v[:, -1, :config.nx//2]) / (2 * config.dy)
dv_dy[:, -1, :config.nx//2] = (data_v[:, 0, :config.nx//2] - data_v[:, -2, config.nx//2:]) / (2 * config.dy)
dv_dy[:, -1, config.nx//2:] = (data_v[:, 0, config.nx//2:] - data_v[:, -2, :config.nx//2]) / (2 * config.dy)

div = du_dx + dv_dy
```

**効果**: **5-10倍高速化**

---

### 3. I/Oの最適化

#### 3.1 `np.memmap()`の使用

**対象**: `azim_mean/azim_2d_calc.py`

```python
# ❌ 遅い実装（現在）
def process_t(t):
    count_2d = config.nx * config.ny
    offset = count_2d * t * 4
    with open(f"{config.input_folder}{varname}.grd", "rb") as f:
        f.seek(offset)
        data = np.fromfile(f, dtype=">f4", count=count_2d)
    data = data.reshape(config.ny, config.nx)

# ✅ 高速化版（ファイル外で一度だけメモリマップ）
data_all = np.memmap(
    f"{config.input_folder}{varname}.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.ny, config.nx),
)

def process_t(t):
    data = data_all[t]  # 高速アクセス
```

**効果**: **2-3倍高速化**

---

### 4. 計算のキャッシュ化

#### 4.1 グリッド計算のキャッシュ

**対象**: 複数のファイル

```python
# ❌ 遅い実装（毎回計算）
def process_t(t):
    cx = center_x_list[t]
    cy = center_y_list[t]

    dX = X - cx
    dY = Y - cy
    dX[dX > 0.5 * config.x_width] -= config.x_width
    dX[dX < -0.5 * config.x_width] += config.x_width

    theta = np.arctan2(dY, dX)
    R = np.sqrt(dX**2 + dY**2)

# ✅ 高速化版（事前計算）
# GridHandlerに追加
class GridHandler:
    def get_polar_coords(self, cx, cy):
        """極座標計算（キャッシュ付き）"""
        key = (cx, cy)
        if not hasattr(self, '_polar_cache'):
            self._polar_cache = {}

        if key not in self._polar_cache:
            dX = self.X - cx
            dY = self.Y - cy
            dX[dX > 0.5 * self.config.x_width] -= self.config.x_width
            dX[dX < -0.5 * self.config.x_width] += self.config.x_width

            R = np.sqrt(dX**2 + dY**2)
            theta = np.arctan2(dY, dX)

            self._polar_cache[key] = (R, theta, dX, dY)

        return self._polar_cache[key]
```

**効果**: **1.2-1.5倍高速化**（繰り返し実行の場合）

---

### 5. Numbaによるコンパイル（上級者向け）

#### 5.1 JITコンパイルの適用

```python
from numba import jit, prange

@jit(nopython=True, parallel=True)
def binned_sum_numba(bin_idx, values, max_bin):
    """Numbaでコンパイルされたビニング処理"""
    result = np.zeros((values.shape[0], max_bin))
    for z in prange(values.shape[0]):
        for i in range(len(bin_idx)):
            result[z, bin_idx[i]] += values[z, i]
    return result

# 使用例
azim_sum_radial = binned_sum_numba(bin_idx, v_radial, max_bin)
```

**効果**: **5-50倍高速化**（ケースによる）

**注意**:
- 初回実行時にコンパイルのオーバーヘッドあり
- すべてのNumPy関数が使えるわけではない

---

### 6. メモリアクセスパターンの最適化

#### 6.1 転置による最適化

```python
# ❌ 非効率（列アクセス）
for i in range(data.shape[1]):
    process(data[:, i])  # 列方向のアクセスは遅い

# ✅ 効率的（行アクセス）
data_T = data.T
for i in range(data_T.shape[0]):
    process(data_T[i])  # 行方向のアクセスは速い
```

**効果**: **1.5-2倍高速化**

---

### 7. プロット処理の最適化

#### 7.1 Matplotlibのバックエンド最適化

```python
# スクリプトの最初に追加
import matplotlib
matplotlib.use('Agg')  # GUIバックエンドを無効化
import matplotlib.pyplot as plt

# さらに高速化
plt.ioff()  # インタラクティブモードをオフ
```

**効果**: **1.2-1.5倍高速化**

#### 7.2 不要な描画処理の削減

```python
# ❌ 遅い
fig, ax = plt.subplots(figsize=(5, 2))
c = ax.contourf(X, Y, data, ...)
cbar = fig.colorbar(c, ax=ax)
cbar.set_ticks([...])
# ... 多くのカスタマイズ

# ✅ 最小限
fig, ax = plt.subplots(figsize=(5, 2), dpi=100)  # DPI指定で高速化
ax.contourf(X, Y, data, ...)
fig.savefig(..., dpi=100)  # 明示的なDPI指定
plt.close(fig)  # 確実にメモリ解放
```

---

## 📈 期待される総合効果

### 計算スクリプト

| 最適化手法 | 対象 | 期待効果 | 実装難易度 |
|----------|------|---------|-----------|
| ループのベクトル化 | azim_wind_calc.py | **10-100倍** | ⭐ 易しい |
| 3D配列ベクトル化 | divergence_calc.py | **5-10倍** | ⭐⭐ 普通 |
| I/O最適化 | azim_2d_calc.py | **2-3倍** | ⭐ 易しい |
| 計算キャッシュ | 複数ファイル | **1.2-1.5倍** | ⭐⭐ 普通 |
| Numbaコンパイル | 重い計算部分 | **5-50倍** | ⭐⭐⭐ 難しい |

### プロットスクリプト

| 最適化手法 | 期待効果 | 実装難易度 |
|----------|---------|-----------|
| バックエンド最適化 | **1.2-1.5倍** | ⭐ 易しい |
| DPI最適化 | **1.1-1.2倍** | ⭐ 易しい |
| メモリ管理 | **1.1-1.3倍** | ⭐ 易しい |

### 総合的な効果予測

```
現在の実行時間を T とすると：

【最小効果】（易しい最適化のみ）
- 計算スクリプト: T → T/15  (15倍高速化)
- プロットスクリプト: T → T/1.5  (1.5倍高速化)

【最大効果】（全ての最適化を適用）
- 計算スクリプト: T → T/100  (100倍高速化)
- プロットスクリプト: T → T/2  (2倍高速化)
```

---

## 🎯 優先順位付き実装ロードマップ

### フェーズ1: クイックウィン（1-2日）
**効果/労力比が最も高い**

1. ✅ `azim_wind_calc.py`のループをベクトル化
   - 期待効果: **10-100倍**
   - 実装時間: 30分

2. ✅ `divergence_calc.py`のz方向ループをベクトル化
   - 期待効果: **5-10倍**
   - 実装時間: 1時間

3. ✅ `azim_2d_calc.py`を`np.memmap()`に変更
   - 期待効果: **2-3倍**
   - 実装時間: 30分

4. ✅ Matplotlibバックエンドの最適化
   - 期待効果: **1.2-1.5倍**
   - 実装時間: 10分

**合計期待効果**: **20-150倍高速化**

---

### フェーズ2: 中期改善（3-5日）

5. ⏳ GridHandlerに極座標計算のキャッシュ機能を追加
   - 期待効果: **1.2-1.5倍**
   - 実装時間: 2-3時間

6. ⏳ 他の計算ファイルにも同様のベクトル化を適用
   - 期待効果: **5-20倍**
   - 実装時間: 1-2日

7. ⏳ 共通処理のユーティリティ化
   - 期待効果: 保守性向上
   - 実装時間: 1日

---

### フェーズ3: 上級最適化（1-2週間）

8. 🔮 Numbaによる重い計算のコンパイル
   - 期待効果: **5-50倍**
   - 実装時間: 3-5日
   - 必要スキル: Numbaの知識

9. 🔮 データ処理パイプラインの見直し
   - 期待効果: **2-5倍**
   - 実装時間: 5-7日

10. 🔮 メモリ使用量の最適化
    - 期待効果: 大規模データ対応
    - 実装時間: 3-5日

---

## 💡 すぐに試せる簡単な最適化

### 1分でできる最適化

```python
# スクリプトの最初に追加
import os
os.environ['OMP_NUM_THREADS'] = '1'  # NumPyの自動並列化を制御
os.environ['MKL_NUM_THREADS'] = '1'  # IntelMKLの並列化を制御

import matplotlib
matplotlib.use('Agg')  # プロット高速化
```

---

## 📊 ベンチマーク例

### 実測例（仮想データ）

```python
# ベンチマークスクリプト
import time
import numpy as np

# テストデータ
nz = 74
n_points = 1000000
max_bin = 5000

bin_idx = np.random.randint(0, max_bin, n_points)
v_radial = np.random.randn(nz, n_points)

# ❌ ループ版
start = time.time()
azim_sum_radial = np.zeros((nz, max_bin))
for i, b in enumerate(bin_idx):
    azim_sum_radial[:, b] += v_radial[:, i]
loop_time = time.time() - start
print(f"ループ版: {loop_time:.2f}秒")

# ✅ ベクトル化版
start = time.time()
azim_sum_radial = np.zeros((nz, max_bin))
np.add.at(azim_sum_radial.T, bin_idx, v_radial.T)
vectorized_time = time.time() - start
print(f"ベクトル化版: {vectorized_time:.2f}秒")

print(f"高速化率: {loop_time / vectorized_time:.1f}倍")
```

**予想結果**:
```
ループ版: 45.23秒
ベクトル化版: 0.52秒
高速化率: 87.0倍
```

---

## 🔧 実装支援ツール

### ベンチマークヘルパー

```python
# utils/benchmark.py
import time
from functools import wraps

def benchmark(func):
    """関数の実行時間を計測するデコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__}: {elapsed:.2f}秒")
        return result
    return wrapper

# 使用例
@benchmark
def process_t(t):
    # 処理内容
    pass
```

---

## 📚 参考資料

### NumPy高速化
- [NumPy Performance Tips](https://numpy.org/doc/stable/user/basics.performance.html)
- [100 numpy exercises](https://github.com/rougier/numpy-100)

### Numba
- [Numba Documentation](https://numba.pydata.org/)
- [Numba vs NumPy comparison](https://numba.pydata.org/numba-doc/latest/user/performance-tips.html)

### プロファイリング
- `line_profiler`: 行ごとの実行時間測定
- `memory_profiler`: メモリ使用量測定
- `py-spy`: 実行中のプロファイリング

---

**作成者**: Claude Code
**バージョン**: 1.0
**最終更新**: 2025-11-25
