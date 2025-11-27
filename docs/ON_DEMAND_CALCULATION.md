# オンデマンド計算による ストレージ節約

## 概要

theta_e（相当温位）やpsi（流線関数）などの派生変数は、データ量が膨大になります。
これらを事前に計算して保存する代わりに、**必要時にその場で計算**することで、
ストレージを大幅に節約できます。

## ストレージ削減効果

### 削減前
```
データサイズ例（config.nt=6, config.nz=74, ny=nx=1024, float32）:
- theta_e: 6 × 74 × 1024 × 1024 × 4 bytes = 1.8 GB
- psi:     6 × 74 × 1024 × 1024 × 4 bytes = 1.8 GB
合計: 3.6 GB
```

### 削減後
```
データサイズ:
- 保存なし: 0 GB
削減量: 3.6 GB (100%削減)
```

**大規模実験（nt=100など）では数十GB〜数百GBの削減が可能！**

## 使用方法

### 1. 相当温位（theta_e）の計算

#### プロットスクリプトでの使用例

**従来の方法（データ読み込み）**:
```python
import numpy as np

# 保存済みデータを読み込む
theta_e = np.load(f"./data/3d/theta_e/t{str(t).zfill(3)}.npy")
```

**新しい方法（オンデマンド計算）**:
```python
import numpy as np
from utils.config import AnalysisConfig
from utils.thermodynamics import calculate_theta_e_from_memmap

config = AnalysisConfig()

# メモリマップを開く
data_tem = np.memmap(
    f"{config.input_folder}ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_pres = np.memmap(
    f"{config.input_folder}ms_pres.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)
data_qv = np.memmap(
    f"{config.input_folder}ms_qv.grd",
    dtype=">f4",
    mode="r",
    shape=(config.nt, config.nz, config.ny, config.nx),
)

# 必要な時刻だけ計算
theta_e = calculate_theta_e_from_memmap(data_tem, data_pres, data_qv, t)
```

#### 既にデータがある場合
```python
from utils.thermodynamics import calculate_theta_e

# tem, pres, qv が既にメモリにある場合
theta_e = calculate_theta_e(tem, pres, qv)
```

### 2. 流線関数（psi）の計算

#### プロットスクリプトでの使用例

**新しい方法（オンデマンド計算）**:
```python
import numpy as np
from utils.config import AnalysisConfig
from utils.streamfunction import calculate_streamfunction_from_memmap

config = AnalysisConfig()

# 渦度データを読み込む（または計算する）
# 渦度は比較的小さいデータなので保存しておく
data_vorticity_z = np.load(f"./data/3d/vorticity_z/vor_t{str(t).zfill(3)}.npy")

# 流線関数を計算
psi = calculate_streamfunction(data_vorticity_z, config.dx, config.dy)
```

#### メモリマップから直接計算
```python
# メモリマップから計算（渦度がメモリマップの場合）
psi = calculate_streamfunction_from_memmap(data_vorticity_z, t, config.dx, config.dy)
```

## 計算スクリプトの扱い

### オプション1: 計算スクリプトを削除

ストレージを完全に節約したい場合:
```bash
# データを保存しないので、calcスクリプトは不要
# rm analysis/spatial/3d/calc/theta_e_calc.py
# rm analysis/spatial/3d/calc/psi_calc.py
```

### オプション2: calcスクリプトを保持（オプション的に実行）

テスト用やキャッシュ目的で保存したい場合もある:
```bash
# 必要に応じて実行
python analysis/spatial/3d/calc/theta_e_calc.py
python analysis/spatial/3d/calc/psi_calc.py
```

calcスクリプトは関数を使うように修正:
```python
# theta_e_calc.py (簡略版)
from utils.thermodynamics import calculate_theta_e_from_memmap
from joblib import Parallel, delayed

def process_t(t):
    theta_e = calculate_theta_e_from_memmap(data_tem, data_pres, data_qv, t)
    np.save(os.path.join(OUTPUT_FOLDER, f"t{str(t).zfill(3)}.npy"), theta_e)

Parallel(n_jobs=config.n_jobs)(
    delayed(process_t)(t) for t in range(config.t_first, config.t_last + 1)
)
```

## パフォーマンス

### 計算時間

**theta_e計算**:
- 計算: ~0.1秒（1024×1024グリッド、74レベル）
- ディスク読み込み: ~0.2-0.5秒

→ オンデマンド計算でも十分高速（特にSSDの場合）

**psi計算（FFT）**:
- 計算: ~0.5-1秒（1024×1024グリッド、74レベル）
- ディスク読み込み: ~0.2-0.5秒

→ やや重いが、プロット作成時のボトルネックにはならない

### メモリ使用量

- 従来: 保存データ分のメモリ不要
- 新方式: 計算時のみ一時的にメモリ使用

→ メモリマップを使えば元データは共有されるので問題なし

## 推奨事項

### 常にオンデマンド計算すべきもの

1. **theta_e（相当温位）**: 計算が軽い、データが大きい
2. **psi（流線関数）**: やや重いがFFTで高速、データが大きい
3. **他の熱力学変数**: 比較的計算が軽い

### 保存しておくべきもの

1. **vorticity_z（渦度）**: 多くの解析で使用、計算がやや重い
2. **divergence（発散）**: 同上
3. **基本変数（u, v, w, tem, pres, qv）**: これらは元データとして必須

## 実装例: プロットスクリプトの修正

### Before（データ読み込み）
```python
# analysis/spatial/3d/plot/theta_e_plot_whole_region.py
theta_e = np.load(f"./data/3d/theta_e/t{str(t).zfill(3)}.npy")
plt.contourf(X, Y, theta_e[z])
```

### After（オンデマンド計算）
```python
# analysis/spatial/3d/plot/theta_e_plot_whole_region.py
from utils.thermodynamics import calculate_theta_e_from_memmap

# メモリマップを開く（スクリプトの初期化部分）
data_tem = np.memmap(...)
data_pres = np.memmap(...)
data_qv = np.memmap(...)

# プロット時に計算
theta_e = calculate_theta_e_from_memmap(data_tem, data_pres, data_qv, t)
plt.contourf(X, Y, theta_e[z])
```

## まとめ

### メリット
✅ **ストレージ大幅削減**: 数GB〜数百GBの削減
✅ **計算も高速**: 現代のCPUでは十分実用的
✅ **メモリ効率**: メモリマップで元データを共有
✅ **柔軟性**: 必要な時だけ計算

### デメリット
⚠️ **毎回計算**: 同じデータを何度も使う場合は遅い
⚠️ **CPU負荷**: I/O待ちがCPU待ちに変わる

### 推奨
- **一度だけ使う**: オンデマンド計算 👍
- **繰り返し使う**: 保存 or メモリキャッシュ 👍
- **ストレージ制約**: オンデマンド計算 👍👍

---

**作成日**: 2025-11-27
**更新**: utils/thermodynamics.py, utils/streamfunction.py 追加
