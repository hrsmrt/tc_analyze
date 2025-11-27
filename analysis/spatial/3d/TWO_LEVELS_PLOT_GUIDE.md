# 2つのZ面プロットスクリプト 使用ガイド

**作成日**: 2025-11-26

---

## 📊 概要

`3d/whole_domain.py`を参考に、2つの異なるZ面のデータを1つの図に重ねてプロットするスクリプトを2種類作成しました。

---

## 🎨 作成したスクリプト

### 1. **whole_domain_two_levels.py** - 塗りつぶし＋線

1つ目のZ面を塗りつぶしcontour、2つ目のZ面を線のcontourで重ねます。

**特徴:**
- ✅ 1つ目のZ面: `contourf`（塗りつぶし、半透明）
- ✅ 2つ目のZ面: `contour`（黒い線）+ ラベル表示
- ✅ 凡例付き
- ✅ 見やすい

**使用方法:**
```bash
# 基本形
python $WORK/tc_analyze/3d/whole_domain_two_levels.py varname z1 z2 $style

# 例1: 地上（z=0）と上層（z=36）の温度
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_tem 0 36 $style

# 例2: 下層（z=9）と上層（z=54）のu風
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_u 9 54 $style

# 例3: 地上と中層の鉛直速度
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_w 0 29 $style
```

**出力先:**
```
./fig/3d/whole_domain_two_levels/{varname}_z{z1}_z{z2}/t000.png
```

**出力イメージ:**
```
┌─────────────────────────────┐
│ t=72h | Fill: z=0.0km |     │
│       | Line: z=5.5km       │
├─────────────────────────────┤
│                             │
│   [カラー塗りつぶし領域]      │
│      + 黒線の等高線          │
│                             │
│   [カラーバー]  [凡例]       │
└─────────────────────────────┘
```

---

### 2. **whole_domain_two_levels_filled.py** - 2つとも塗りつぶし（比較表示）

2つのZ面をそれぞれ異なるカラーマップで半透明に重ねます。左右比較形式。

**特徴:**
- ✅ 左側: 1つ目のZ面のみ
- ✅ 右側: 2つのZ面を重ねて表示（異なるカラーマップ + 半透明）
- ✅ 比較しやすい

**使用方法:**
```bash
# 基本形
python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py varname z1 z2 $style

# 例1: 地上と上層の温度を比較
python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_tem 0 36 $style

# 例2: 下層と上層のu風を比較
python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_u 9 54 $style
```

**出力先:**
```
./fig/3d/whole_domain_two_levels_filled/{varname}_z{z1}_z{z2}/t000.png
```

**出力イメージ:**
```
┌─────────────────────────────────────────────────┐
│       t=72h | ms_tem                            │
├──────────────────────┬──────────────────────────┤
│  z=0.0km のみ        │  z=0.0km + z=5.5km       │
│                      │                          │
│  [カラー塗りつぶし]    │  [2色を半透明で重ねた図] │
│                      │                          │
│  [カラーバー]         │  [カラーバー]            │
└──────────────────────┴──────────────────────────┘
```

---

## 📋 引数の説明

### 共通引数

| 引数 | 説明 | 例 |
|------|------|-----|
| `varname` | 変数名 | `ms_tem`, `ms_u`, `ms_v`, `ms_w`, `ms_rh`, `ms_qv` など |
| `z1` | 1つ目のZ面インデックス（0-73） | `0` (地上), `9`, `17`, `23`, `29`, `36`, `42`, `48`, `54`, `60` |
| `z2` | 2つ目のZ面インデックス（0-73） | `36` (約5.5km) など |
| `$style` | Matplotlibスタイル（オプション） | プレゼンテーション用スタイルなど |

### Z面インデックスの目安

| インデックス | 高度（おおよそ） |
|-------------|----------------|
| 0 | 地上 (0 km) |
| 9 | 下層 (約1 km) |
| 17 | 下層 (約2 km) |
| 23 | 中層 (約3 km) |
| 29 | 中層 (約4 km) |
| 36 | 上層 (約5.5 km) |
| 42 | 上層 (約7 km) |
| 48 | 上層 (約9 km) |
| 54 | 上層 (約11 km) |
| 60 | 上層 (約13 km) |

正確な高度は`vgrid.txt`を参照してください。

---

## 🎯 使い分けガイド

### whole_domain_two_levels.py を使う場合

✅ **おすすめの用途:**
- 1つの変数を主に見たい＋もう1つの高度の値も参考にしたい
- 等高線の値を読み取りたい
- 2つの高度の違いを定性的に理解したい

✅ **例:**
```bash
# 地上気温の分布を見つつ、上層の気温も確認
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_tem 0 36 $style

# 下層のu風を見つつ、上層のu風の等高線も確認
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_u 9 54 $style
```

---

### whole_domain_two_levels_filled.py を使う場合

✅ **おすすめの用途:**
- 2つの高度を並べて比較したい
- 重なりを視覚的に確認したい
- プレゼンテーション用に比較図を作りたい

✅ **例:**
```bash
# 地上と上層の温度を左右比較
python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_tem 0 36 $style

# 下層と上層のw（鉛直速度）を比較
python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_w 9 54 $style
```

---

## 🔧 カスタマイズ方法

### 2つ目のZ面の線の色を変更

`whole_domain_two_levels.py`の79行目を編集：

```python
# 現在: 黒い線
cs = ax.contour(..., colors='black', ...)

# 白い線に変更
cs = ax.contour(..., colors='white', ...)

# 緑の線に変更
cs = ax.contour(..., colors='green', ...)

# カラーマップを使用
cs = ax.contour(..., cmap='viridis', ...)
```

### 透明度の調整

`whole_domain_two_levels.py`の68行目を編集：

```python
# 現在: alpha=0.8（80%不透明）
cf = ax.contourf(..., alpha=0.8)

# より透明に（50%不透明）
cf = ax.contourf(..., alpha=0.5)

# 完全に不透明
cf = ax.contourf(..., alpha=1.0)
```

### 線の太さを変更

`whole_domain_two_levels.py`の81行目を編集：

```python
# 現在: linewidths=1.5
cs = ax.contour(..., linewidths=1.5, ...)

# より太く
cs = ax.contour(..., linewidths=2.5, ...)

# より細く
cs = ax.contour(..., linewidths=0.8, ...)
```

---

## 📊 対応している変数

両方のスクリプトは、元の`whole_domain.py`と同じ変数に対応しています：

| 変数名 | 説明 | カラーマップ | レベル |
|--------|------|------------|--------|
| `ms_u` | 東西風速 [m/s] | bwr | -40 ~ 40 |
| `ms_v` | 南北風速 [m/s] | bwr | -40 ~ 40 |
| `ms_w` | 鉛直風速 [m/s] | bwr | -4 ~ 4 |
| `ms_tem` | 温度 [K] | rainbow | 自動 or 295-305 (z=0) |
| `ms_rh` | 相対湿度 [-] | rainbow | 0 ~ 1.1 |
| `ms_qv` | 水蒸気混合比 [kg/kg] | rainbow | 自動 or 0.005-0.025 (z=0) |
| その他 | - | rainbow | 自動 |

---

## ✅ 最適化機能

両方のスクリプトに以下の最適化が適用されています：

1. ✅ **Matplotlibバックエンド最適化**: `matplotlib.use('Agg')`
2. ✅ **I/O最適化**: `np.memmap()`でメモリマップドI/O
3. ✅ **並列処理**: `joblib.Parallel`で高速化

---

## 💡 使用例

### 例1: 台風の上下層の風の違いを見る

```bash
# 下層（約1km）と上層（約11km）のu風
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_u 9 54 $style
```

### 例2: 地上と上層の温度分布を比較

```bash
# 地上と上層（約5.5km）の温度を左右比較
python $WORK/tc_analyze/3d/whole_domain_two_levels_filled.py ms_tem 0 36 $style
```

### 例3: 鉛直速度の高度による違い

```bash
# 下層（約2km）と上層（約9km）の鉛直速度
python $WORK/tc_analyze/3d/whole_domain_two_levels.py ms_w 17 48 $style
```

---

## 🎉 まとめ

| スクリプト | 表示形式 | 用途 |
|----------|---------|------|
| `whole_domain_two_levels.py` | 塗りつぶし＋線 | 等高線の値を読み取りたい場合 |
| `whole_domain_two_levels_filled.py` | 左右比較 | 2つの高度を並べて比較したい場合 |

どちらも最適化済みで、高速に動作します！

---

**作成者**: Claude Code
**バージョン**: 1.0
**最終更新**: 2025-11-26
