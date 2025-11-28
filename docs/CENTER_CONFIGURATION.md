# 中心座標の設定と管理ガイド

**最終更新**: 2025-11-29

本ドキュメントでは、TC中心座標の計算、設定、読み込み、メタデータ管理について説明します。

**v2.3.0の新機能（2025-11-29）**:
- メソッド別スクリプトの分離（weighted.py / smoothed.py）
- center_configsの拡張（メソッド別ファイル名管理）
- AnalysisConfigの自動読み込み機能
- メタデータへのcreated_at追加

---

## 目次

1. [概要](#概要)
2. [中心座標の種類](#中心座標の種類)
3. [計算パラメータ](#計算パラメータ)
4. [設定ファイルの構成](#設定ファイルの構成)
5. [中心座標の計算](#中心座標の計算)
6. [中心座標の読み込み](#中心座標の読み込み)
7. [メタデータの確認と編集](#メタデータの確認と編集)
8. [トラブルシューティング](#トラブルシューティング)
9. [v2.3.0の更新（2025-11-29）](#v230の更新2025-11-29)
   - [メソッド別スクリプトの分離](#メソッド別スクリプトの分離)
   - [center_configsの拡張](#center_configsの拡張)
   - [AnalysisConfigの自動読み込み](#analysisconfigの自動読み込み)
   - [メタデータの強化: created_at](#メタデータの強化-created_at)
   - [複数パラメータの管理](#複数パラメータの管理)
   - [旧スクリプトとの互換性](#旧スクリプトとの互換性)

---

## 概要

TC解析では、以下の2種類の中心座標を使用します：

- **SS SLP中心** (2D): 海面気圧の最小値から算出される中心位置
- **MS PRES中心** (3D): 各高度面の気圧最小値から算出される中心位置

v2.2.0から、中心座標ファイルの管理が`setting.json`で一元化され、パラメータの異なる複数の中心座標を簡単に切り替えられるようになりました。

---

## 中心座標の種類

### SS SLP (Sea Surface Low Pressure) 中心

- **形状**: `(nt, 2)` - 時間ステップごとのx, y座標
- **用途**: 2次元解析、基本的な中心追跡
- **計算方法**: 海面気圧場の最小値を重み付き重心法で精密化

### MS PRES (Model Surface Pressure) 中心

- **形状**: `(nt, nz, 2)` - 時間・高度ごとのx, y座標
- **用途**: 3次元解析、高度依存の中心追跡
- **計算方法**: SS SLP中心の周辺で各高度の気圧最小値を探索

---

## 中心特定方法

TC中心の特定には、2つの方法を選択できます。

### 利用可能な方法

| 方法 | 説明 | 推奨用途 |
|------|------|---------|
| **weighted_centroid** | 重み付き重心法（反復精密化） | ノイズの少ないデータ、高精度が必要な場合（デフォルト） |
| **smoothed_minimum** | ガウシアン平滑化 + 極小点探索 | ノイズの多いデータ、広域的な中心を捉えたい場合 |

### weighted_centroid (重み付き重心法)

**原理**: 気圧場の最小値周辺で、気圧を重みとした重心を反復計算し、中心位置を精密化します。

**特徴**:
- 高精度な中心位置の特定
- 局所的な気圧構造に敏感
- ノイズの影響を受けやすい

**パラメータ**:
- `r_refine`: 重み付き重心計算の探索半径（デフォルト: 100 km）
- `r_search`: 初期探索半径（MS PRESのみ、デフォルト: 200 km）

### smoothed_minimum (平滑化後の極小点法)

**原理**: ガウシアンフィルタで気圧場を平滑化し、平滑化後の最小値を中心とします。

**特徴**:
- ノイズに強い
- 広域的な気圧パターンを捉える
- 精度はやや低い（オプションで精密化可能）

**パラメータ**:
- `r_smooth`: 平滑化半径（デフォルト: 500 km）
- `--refine-after-smooth`: 平滑化後に重み付き重心法で精密化（オプション）

## 計算パラメータ

### パラメータの意味

| パラメータ | 意味 | デフォルト値 | 使用メソッド |
|-----------|------|------------|-------------|
| **r_refine** | 重み付き重心計算の探索半径 | 100 km | weighted_centroid, smoothed_minimum（精密化時） |
| **r_search** | 初期探索半径（MS PRESのみ） | 200 km | weighted_centroid (MS PRESのみ) |
| **r_smooth** | ガウシアン平滑化の半径 | 500 km | smoothed_minimum |

#### r_refine (Refinement Radius)

重み付き重心法で中心位置を精密化する際の探索半径。小さいほど局所的な最小値を捉えやすいが、ノイズに敏感になります。

#### r_search (Search Radius)

MS PRES中心計算時に、SS SLP中心からどれだけの範囲内で気圧最小値を探すかを指定します（weighted_centroid メソッドのみ）。これにより、遠方の別の低気圧システムを誤って検出することを防ぎます。

#### r_smooth (Smoothing Radius)

ガウシアンフィルタの平滑化半径（smoothed_minimum メソッドのみ）。大きいほど広域的なパターンを捉えますが、中心位置の精度が低下します。

---

## 設定ファイルの構成

### setting.json の設定

```json
{
  "nt": 145,
  "glevel": 10,
  "triangle_size": 2048000.0,
  "dt_output": 3600,
  "input_folder": "./input/",
  "vgrid_filepath": "./vgrid.txt",
  "data_dir": "./data",
  "fig_dir": "./fig",
  "n_jobs": 8,

  "center_method": "weighted_centroid",
  "center_configs": {
    "ss_slp": "center.npz",
    "ms_pres": "center.npz"
  }
}
```

### center_method の説明

- **オプショナル**: 指定しない場合、デフォルト値 `"weighted_centroid"` が使用されます
- **値**: `"weighted_centroid"` または `"smoothed_minimum"`
- **用途**: TC中心の特定方法を選択します
- **コマンドライン**: `--method` オプションで上書き可能

### center_configs の説明

- **オプショナル**: 指定しない場合、デフォルト値 `"center.npz"` が使用されます
- **ss_slp**: SS SLP中心座標ファイルの名前
- **ms_pres**: MS PRES中心座標ファイルの名前
- **用途**: 異なるパラメータで計算した中心座標を使い分ける場合に便利

### 使用例

#### 同じファイル名を使う場合（デフォルト）

```json
"center_configs": {
  "ss_slp": "center.npz",
  "ms_pres": "center.npz"
}
```

パラメータを変更しても同じファイルに上書きされます。

#### 異なるファイル名を使う場合（複数バージョン管理）

```json
"center_configs": {
  "ss_slp": "center_rrefine100km.npz",
  "ms_pres": "center_rsearch200km_rrefine100km.npz"
}
```

異なるパラメータで計算した結果を別ファイルとして保存し、必要に応じて切り替えられます。

---

## 中心座標の計算

### SS SLP中心の計算

#### weighted_centroid メソッド（デフォルト）

```bash
# デフォルトパラメータ（r_refine=100km）
python analysis/center/ss_slp/calc/ss_slp_center_calc.py

# r_refineを指定
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --r-refine 150e3

# メソッドを明示的に指定
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --method weighted_centroid
```

#### smoothed_minimum メソッド

```bash
# デフォルトパラメータ（r_smooth=500km）
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --method smoothed_minimum

# r_smoothを指定
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --method smoothed_minimum --r-smooth 600e3

# 平滑化後に精密化
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --method smoothed_minimum --refine-after-smooth
```

**出力ファイル**: `data/center/ss_slp/[center_configs["ss_slp"]で指定したファイル名]`

### MS PRES中心の計算

#### weighted_centroid メソッド（デフォルト）

```bash
# デフォルトパラメータ（r_search=200km, r_refine=100km）
python analysis/center/ms_pres/calc/ms_pres_center_calc.py

# パラメータを指定
python analysis/center/ms_pres/calc/ms_pres_center_calc.py --r-search 250e3 --r-refine 150e3

# z範囲を指定
python analysis/center/ms_pres/calc/ms_pres_center_calc.py --z-first 0 --z-last 50 --r-search 200e3
```

#### smoothed_minimum メソッド

```bash
# デフォルトパラメータ（r_smooth=500km）
python analysis/center/ms_pres/calc/ms_pres_center_calc.py --method smoothed_minimum

# r_smoothを指定
python analysis/center/ms_pres/calc/ms_pres_center_calc.py --method smoothed_minimum --r-smooth 600e3

# 平滑化後に精密化
python analysis/center/ms_pres/calc/ms_pres_center_calc.py --method smoothed_minimum --refine-after-smooth
```

**出力ファイル**: `data/center/ms_pres/[center_configs["ms_pres"]で指定したファイル名]`

### 保存されるメタデータ

npzファイルには以下のメタデータが自動的に保存されます：

**共通メタデータ:**
- `center`: 中心座標配列
  - SS SLP: `(nt, 2)`
  - MS PRES: `(nt, nz, 2)`
- `method`: 使用した中心特定方法（`"weighted_centroid"` または `"smoothed_minimum"`）
- `actual_iterations`: 実際の反復回数
  - SS SLP: `(nt,)`
  - MS PRES: `(nt, nz)`

**weighted_centroid メソッドの追加メタデータ:**
- `r_refine`: 使用したr_refine値
- `r_search`: 使用したr_search値（MS PRESのみ）
- `max_iterations`: 最大反復回数
- `convergence_threshold_x/y`: 収束判定閾値

**smoothed_minimum メソッドの追加メタデータ:**
- `r_smooth`: 使用したr_smooth値
- `refine_after_smooth`: 平滑化後の精密化の有無（True/False）
- （精密化を有効にした場合、weighted_centroidと同じメタデータも保存）

**MS PRES固有のメタデータ:**
- `z_first`, `z_last`: 処理したz範囲

---

## 中心座標の読み込み

### Pythonコードでの読み込み

#### 方法1: load_center_coordinates() を使用（推奨）

```python
from utils.config import AnalysisConfig
from utils.center import load_center_coordinates

config = AnalysisConfig()

# SS SLP中心を読み込み（2D）
ss_x, ss_y, ss_meta = load_center_coordinates(config, "ss_slp")
# ss_x.shape = (nt,), ss_y.shape = (nt,)

# MS PRES中心を読み込み（3D）
ms_x, ms_y, ms_meta = load_center_coordinates(config, "ms_pres")
# ms_x.shape = (nt, nz), ms_y.shape = (nt, nz)

# メタデータを確認
print(f"r_refine: {ss_meta['r_refine']} m")
print(f"Mean iterations: {ss_meta['actual_iterations'].mean()}")
```

#### 方法2: AnalysisConfigで直接指定（既存の方法）

```python
from utils.config import AnalysisConfig

# SS SLP中心を使用（デフォルト）
config = AnalysisConfig()
cx = config.center_x  # shape: (nt,)
cy = config.center_y  # shape: (nt,)

# MS PRES中心を使用
config = AnalysisConfig(center_type="3d", center_path="center/ms_pres")
cx = config.center_x  # shape: (nt, nz)
cy = config.center_y  # shape: (nt, nz)
```

### .npy/.npz両方に対応

`load_center_coordinates()`は自動的に.npy/.npzの両方に対応します：

1. `center_configs`で指定したファイル名を試す
2. 見つからない場合、拡張子を変えて再試行（.npz ↔ .npy）
3. それでも見つからない場合、エラー

---

## メタデータの確認と編集

### CLIコマンドでの確認

```bash
# SS SLP中心のメタデータを確認
tc-analyze center inspect ss_slp

# MS PRES中心のメタデータを確認
tc-analyze center inspect ms_pres

# 詳細情報を表示
tc-analyze center inspect ss_slp --verbose
```

**出力例:**
```
🔍 Inspecting ss_slp center coordinates

  File: data/center/ss_slp/center.npz
  Format: .npz

📍 Center Coordinates:
  Shape: (145, 2)
  Type: 2D center (nt=145)
  X range: [1200.50, 1350.75] km
  Y range: [1100.25, 1250.80] km

📊 Metadata:
  r_refine                      : 100000 m (100.0 km)
  actual_iterations             : mean=5.23, max=15
  max_iterations                : 100

✓ Inspection complete
```

### メタデータの追加・編集

```bash
# 対話的にメタデータを編集
tc-analyze data annotate center/ss_slp/center.npz
```

対話メニューで以下の操作が可能：
- **[a] Add**: 説明文、メモ、作成者名などを追加
- **[e] Edit**: 既存のメタデータを編集
- **[d] Delete**: 不要なメタデータを削除
- **[s] Save**: 変更を保存（自動バックアップ作成）
- **[q] Quit**: 変更を破棄して終了

**使用例:**
```
Choose an option: a
Enter key name: description
Value type: string
Enter value: SS SLP center with r_refine=100km, calculated on 2025-01-15

Choose an option: a
Enter key name: notes
Value type: string
Enter value: Excellent convergence, suitable for publication

Choose an option: s
Save changes? [y/N]: y
  Created backup: center.npz.backup
✓ Saved changes to center.npz
```

---

## トラブルシューティング

### ファイルが見つからない

**エラー:**
```
FileNotFoundError: Center file not found: data/center/ss_slp/center.npz
```

**解決方法:**
```bash
# 中心座標を計算
python analysis/center/ss_slp/calc/ss_slp_center_calc.py

# または setting.json の center_configs を確認
tc-analyze config show | grep center_configs
```

### パラメータが分からない

**解決方法:**
```bash
# メタデータを確認
tc-analyze center inspect ss_slp
```

### 異なるパラメータを試したい

**方法1: 同じファイルに上書き**
```bash
# 新しいパラメータで計算（ファイルを上書き）
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --r-refine 150e3
```

**方法2: 別ファイルとして保存**
```json
// setting.json を編集
"center_configs": {
  "ss_slp": "center_rrefine150km.npz"  // 別ファイル名に変更
}
```
```bash
# 新しいパラメータで計算（別ファイルとして保存）
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --r-refine 150e3
```

### 古い.npyファイルを使いたい

`load_center_coordinates()`は自動的に.npyファイルも読み込めます：

```json
// setting.json
"center_configs": {
  "ss_slp": "center.npy"  // .npyでも.npzでもOK
}
```

または、.npz形式に変換することを推奨します（メタデータを保存できるため）：

```python
import numpy as np

# .npyファイルを読み込み
center = np.load("data/center/ss_slp/center.npy")

# メタデータ付きで.npz形式で保存
np.savez(
    "data/center/ss_slp/center.npz",
    center=center,
    r_refine=100000.0,
    description="Converted from legacy .npy file"
)
```

---

## ベストプラクティス

### 1. パラメータをメタデータに記録

計算パラメータは自動的にnpzファイルに保存されますが、追加の情報を記録しておくと便利です：

```bash
tc-analyze data annotate center/ss_slp/center.npz
# descriptionに計算日時、目的、品質などを記録
```

### 2. 複数バージョンの管理

異なるパラメータで試す場合は、setting.jsonで切り替えるのが便利：

```json
// テスト用
"center_configs": {
  "ss_slp": "center_test.npz"
}

// 本番用
"center_configs": {
  "ss_slp": "center_final.npz"
}
```

### 3. バックアップの活用

`tc-analyze data annotate`は自動的に`.backup`ファイルを作成するので、誤って上書きした場合も復元できます：

```bash
# バックアップから復元
cp data/center/ss_slp/center.npz.backup data/center/ss_slp/center.npz
```

---

## v2.3.0の更新（2025-11-29）

### メソッド別スクリプトの分離

中心計算のメソッド（weighted_centroid / smoothed_minimum）ごとに専用スクリプトを用意しました。

#### 新しいファイル構成

**SS SLP中心計算:**
```
analysis/center/ss_slp/calc/
├── weighted.py          # weighted_centroid法専用
├── smoothed.py          # smoothed_minimum法専用
└── ss_slp_center_calc.py  # 統合スクリプト（互換性維持）
```

**MS PRES中心計算:**
```
analysis/center/ms_pres/calc/
├── weighted.py          # weighted_centroid法専用
├── smoothed.py          # smoothed_minimum法専用
└── ms_pres_center_calc.py  # 統合スクリプト（互換性維持）
```

#### 使用例

```bash
# SS SLP中心 - weighted_centroid法
python analysis/center/ss_slp/calc/weighted.py --r-refine 150e3

# SS SLP中心 - smoothed_minimum法
python analysis/center/ss_slp/calc/smoothed.py --r-smooth 500e3 --refine

# MS PRES中心 - weighted_centroid法
python analysis/center/ms_pres/calc/weighted.py --z-first 0 --z-last 20

# MS PRES中心 - smoothed_minimum法
python analysis/center/ms_pres/calc/smoothed.py --z-first 0 --z-last 20 --r-smooth 600e3
```

### center_configsの拡張

setting.jsonの`center_configs`に、メソッド別のファイル名を指定できるようになりました：

```json
{
  "center_configs": {
    "ss_slp": "center.npz",
    "ss_slp_weighted": "weighted_center.npz",
    "ss_slp_smoothed": "smoothed_center.npz",
    "ms_pres": "center.npz",
    "ms_pres_weighted": "weighted_center.npz",
    "ms_pres_smoothed": "smoothed_center.npz"
  }
}
```

**キーの命名規則:**
- `{type}`: デフォルトファイル（例: `ss_slp`）
- `{type}_weighted`: weighted_centroid法の出力（例: `ss_slp_weighted`）
- `{type}_smoothed`: smoothed_minimum法の出力（例: `ss_slp_smoothed`）

### AnalysisConfigの自動読み込み

`AnalysisConfig`が`center_configs`から適切なファイル名を自動的に読み取るようになりました。

**読み込み優先順位:**
1. `{type}_weighted` → `weighted_center.npz`
2. `{type}` → `center.npz`
3. `{type}_smoothed` → `smoothed_center.npz`
4. フォールバック: `center.npz` > `center.npy` > `x.txt/y.txt`

**例:**
```python
from utils.config import AnalysisConfig

# デフォルトでcenter/ss_slpから読み込み
config = AnalysisConfig()

# 自動的に以下の順で探索:
# 1. data/center/ss_slp/weighted_center.npz
# 2. data/center/ss_slp/center.npz
# 3. data/center/ss_slp/smoothed_center.npz
# 4. data/center/ss_slp/center.npy
# 5. data/center/ss_slp/x.txt, y.txt

# 最初に見つかったファイルを自動的に読み込む
x_center = config.center_x  # shape: (nt,)
y_center = config.center_y  # shape: (nt,)
```

### メタデータの強化: created_at

全ての中心計算スクリプトに**作成時刻**を記録するようになりました。

**形式:**
- ISO 8601形式（UTC）: `"2025-11-29T12:34:56.789123Z"`
- `datetime.datetime.utcnow().isoformat() + "Z"`

**メタデータ例:**
```python
{
    "center": array([[x1, y1], [x2, y2], ...]),
    "method": "weighted_centroid",
    "created_at": "2025-11-29T12:34:56.789123Z",  # ← 追加
    "r_refine": 100000.0,
    "max_iterations": 100,
    "actual_iterations": array([3, 4, 3, ...]),
    ...
}
```

**利点:**
1. **再現性**: ファイルをコピー/移動しても作成時刻が保持される
2. **トレーサビリティ**: いつ、どのパラメータで実行したかの完全な記録
3. **CLIツール対応**: `tc-analyze data info`で作成時刻を確認可能
4. **科学的ベストプラクティス**: 研究データには作成時刻を含めるのが標準

**確認方法:**
```bash
tc-analyze data info data/center/ss_slp/weighted_center.npz --config run/setting.json

# 出力例:
# File: data/center/ss_slp/weighted_center.npz
# Format: NPZ (NumPy compressed archive)
# Created: 2025-11-29T12:34:56.789123Z
# Method: weighted_centroid
# ...
```

### 複数パラメータの管理

異なるパラメータで計算した中心座標を同時に管理できます：

```bash
# パラメータ1: r_refine=100km
python analysis/center/ss_slp/calc/weighted.py --r-refine 100e3
# → data/center/ss_slp/weighted_center.npz

# パラメータ2: r_refine=150km（別ファイルに保存）
python analysis/center/ss_slp/calc/weighted.py --r-refine 150e3
# setting.jsonを変更してファイル名を変える
# "ss_slp_weighted": "weighted_center_r150km.npz"

# パラメータ3: smoothed_minimum法
python analysis/center/ss_slp/calc/smoothed.py --r-smooth 500e3
# → data/center/ss_slp/smoothed_center.npz
```

### 旧スクリプトとの互換性

旧来の統合スクリプトも引き続き使用可能です：

```bash
# 旧来の方法（まだ動作します）
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --method weighted_centroid
python analysis/center/ss_slp/calc/ss_slp_center_calc.py --method smoothed_minimum
```

ただし、新しいメソッド別スクリプトの使用を推奨します：
- パラメータが明確
- 各メソッドに特化したオプション
- ファイル名の自動管理

---

## 参考情報

### 関連ドキュメント

- [COMMAND_REFERENCE.md](../COMMAND_REFERENCE.md) - コマンドの詳細な使い方
- [ARCHITECTURE.md](../ARCHITECTURE.md) - システムアーキテクチャ
- [README.md](../README.md) - プロジェクト概要

### 関連スクリプト

**SS SLP中心計算:**
- `analysis/center/ss_slp/calc/weighted.py` - weighted_centroid法（推奨）
- `analysis/center/ss_slp/calc/smoothed.py` - smoothed_minimum法（推奨）
- `analysis/center/ss_slp/calc/ss_slp_center_calc.py` - 統合スクリプト（互換性維持）

**MS PRES中心計算:**
- `analysis/center/ms_pres/calc/weighted.py` - weighted_centroid法（推奨）
- `analysis/center/ms_pres/calc/smoothed.py` - smoothed_minimum法（推奨）
- `analysis/center/ms_pres/calc/ms_pres_center_calc.py` - 統合スクリプト（互換性維持）

**ユーティリティ:**
- `utils/config.py` - AnalysisConfig（中心座標自動読み込み）
- `utils/center.py` - 中心検出アルゴリズム
- `tc_analyze/commands/center.py` - 中心座標CLIコマンド
- `tc_analyze/commands/data.py` - データ管理CLIコマンド

---

**最終更新**: 2025-11-29
