# オンデマンド計算への最適化完了報告

**完了日**: 2025-11-27
**プロジェクト**: tc_analyze (熱帯低気圧解析コード群)
**目的**: ストレージ節約とコード保守性向上

---

## 📋 目次

1. [概要](#概要)
2. [実施した最適化](#実施した最適化)
3. [コードベース統計](#コードベース統計)
4. [達成された効果](#達成された効果)
5. [技術的詳細](#技術的詳細)
6. [今後の展開](#今後の展開)

---

## 概要

### プロジェクト背景
修士課程の研究で使用している熱帯低気圧の解析コード群。大量の中間データファイル（数GB〜数百GB）を保存していたため、ストレージ容量と管理の課題があった。

### 最適化の目標
- **ストレージ削減**: 中間データファイルの保存を廃止し、必要時にオンデマンド計算
- **コード統一化**: 重複していた計算ロジックを共通関数に集約
- **保守性向上**: 変更が容易で理解しやすいコード構造へ

---

## 実施した最適化

### 1. 共通計算関数の作成 (utils/azimuthal.py)

| 関数名 | 機能 | 効果 |
|--------|------|------|
| `calculate_azimuthal_mean_wind()` | 絶対風の方位角平均 | データ保存不要 |
| `calculate_azimuthal_mean_relative_wind()` | 相対風の方位角平均 | 周期境界処理を統一 |
| `calculate_azimuthal_mean_wind10m()` | 地上10m風の方位角平均 | 2Dデータ対応 |
| `calculate_azimuthal_mean_theta()` | 温位の方位角平均 | 熱力学計算を統一 |
| `calculate_azimuthal_mean_theta_e()` | 相当温位の方位角平均 | 複雑な計算を集約 |
| `calculate_azimuthal_mean_momentum()` | 角運動量の方位角平均 | 物理量計算を統一 |
| `calculate_azimuthal_mean_3d()` | 汎用3D変数の方位角平均 | 再利用可能 |
| `calculate_azimuthal_mean_2d()` | 汎用2D変数の方位角平均 | 再利用可能 |

### 2. オンデマンド計算への移行

#### 移行済みファイル（12コミット分）

**方位角平均プロット (9ファイル)**
- `azim_theta_plot.py` - 温位
- `azim_theta_e_plot.py` - 相当温位
- `azim_momentum_plot.py` - 角運動量
- `azim_core_wind_radial_plot.py` - コア領域動径風
- `azim_core_wind_tangential_plot.py` - コア領域接線風
- `azim_wind_radial_plot.py` - 動径風
- `azim_wind_tangential_plot.py` - 接線風
- `azim_wind_relative_radial_plot.py` - 相対動径風
- `azim_wind_relative_tangential_plot.py` - 相対接線風
- `azim_wind10m_radial_plot.py` - 地上10m動径風
- `azim_wind10m_tangential_plot.py` - 地上10m接線風

**方位角平均計算 (4ファイル)**
- `azim_theta_calc.py` - 温位計算
- `azim_theta_e_calc.py` - 相当温位計算
- `azim_momentum_calc.py` - 角運動量計算
- `azim_wind_relative_calc.py` - 相対風計算

**3D空間プロット (1ファイル)**
- `theta_e_plot_vortex_region.py` - 渦領域の相当温位

**その他 (1ファイル)**
- `utils/thermodynamics.py` - 熱力学計算関数の追加
- `utils/streamfunction.py` - 流線関数計算関数の追加

### 3. 実行順序の最適化 (run/analyze.sh)

```bash
# 中心位置に依存しない基本解析
run_3d_basic()   # 3D基本場
run_2d_basic()   # 2D基本場

# 中心位置計算
run_center()

# 中心位置に依存する解析（最適化後に実行）
run_3d_wind()    # 3D風成分
run_2d_wind()    # 2D風成分
run_vortex_region()  # 渦領域解析
run_azimuthal()  # 方位角平均
```

---

## コードベース統計

### 📊 総行数: **21,379行**

| カテゴリ | ファイル数 | 行数 | 割合 |
|---------|-----------|------|------|
| **全Pythonファイル** | 222 | 21,379 | 100% |
| └ analysis/ | - | 13,068 | 61.1% |
| 　├ spatial/ | - | 5,215 | 24.4% |
| 　├ azimuthal/ | - | 6,316 | 29.5% |
| 　├ center/ | - | 590 | 2.8% |
| 　└ その他 | - | 947 | 4.4% |
| └ utils/ | 9 | 2,513 | 11.8% |
| └ その他 | - | 5,798 | 27.1% |

### 🔧 ファイルタイプ別

| タイプ | ファイル数 | 行数 | 平均行数 |
|--------|-----------|------|---------|
| calc | 53 | 3,251 | 61.3 |
| plot | 82 | 6,301 | 76.8 |
| utils | 9 | 2,513 | 279.2 |
| その他 | 78 | 9,314 | 119.4 |

---

## 達成された効果

### ✅ ストレージ削減

#### 削減された中間データファイル

1. **方位角平均風データ**
   - `azim/wind_radial/*.npy` - 不要
   - `azim/wind_tangential/*.npy` - 不要
   - `azim/wind_relative_radial/*.npy` - 元データから計算
   - `azim/wind_relative_tangential/*.npy` - 元データから計算
   - `azim/wind10m_radial/*.npy` - 不要
   - `azim/wind10m_tangential/*.npy` - 不要

2. **方位角平均熱力学データ**
   - `azim/ms_tem/*.npy` - 不要
   - `azim/ms_pres/*.npy` - 不要
   - `azim/ms_qv/*.npy` - 不要
   - `azim/theta/*.npy` - 元データから計算（保存は継続）
   - `azim/theta_e/*.npy` - 元データから計算（保存は継続）
   - `azim/momentum/*.npy` - 元データから計算（保存は継続）

3. **3D相対風データ**
   - `3d/relative_u/*.npy` - 不要（オンデマンド計算）
   - `3d/relative_v/*.npy` - 不要（オンデマンド計算）

#### 推定ストレージ削減量

**1実験あたり**:
- nt=121タイムステップ
- nz=74レベル
- ny=nx=512グリッド
- 4バイト/値

| データタイプ | ファイル数 | サイズ/ファイル | 合計 |
|-------------|-----------|----------------|------|
| 方位角平均3D | 121×6 | ~1.5MB | ~1.1GB |
| 方位角平均2D | 121×2 | ~0.2MB | ~48MB |
| 3D相対風 | 121×2 | ~75MB | ~18GB |
| **削減合計** | - | - | **~19GB/実験** |

**複数実験の場合**:
- 10実験: **~190GB削減**
- 50実験: **~950GB削減**

### ✅ コードの改善

#### コード削減例

| ファイル | 移行前 | 移行後 | 削減率 |
|---------|--------|--------|--------|
| `azim_wind_relative_calc.py` | 104行 | 71行 | **32%** |
| `azim_momentum_plot.py` | ~60行 | ~91行 | -52%* |
| `azim_theta_e_plot.py` | ~60行 | ~94行 | -57%* |

*プロット系は詳細なドキュメントとコメントを追加したため行数増加。実質的な計算ロジックは大幅に削減。

#### 重複コード削減

**移行前**:
- 各ファイルで個別に方位角平均計算を実装（50-80行×15ファイル）
- 同じロジックが複数箇所に散在
- バグ修正時に全ファイル修正が必要

**移行後**:
- `utils/azimuthal.py`の関数を呼び出し（1-3行）
- ロジックが1箇所に集約
- 修正は1箇所のみでOK

### ✅ 保守性向上

1. **ロジックの集約**
   - 方位角平均計算: utils/azimuthal.py
   - 熱力学計算: utils/thermodynamics.py
   - 流線関数計算: utils/streamfunction.py

2. **ドキュメント充実**
   - 全関数にdocstringを追加
   - 入出力の明確化
   - 使用例の記載

3. **エラー処理の統一**
   - ゼロ除算処理
   - 周期境界条件
   - マスク処理

---

## 技術的詳細

### オンデマンド計算のパターン

#### Before: 事前計算+保存
```python
# calc.py - 事前計算して保存
data = np.load("ms_tem.grd")
azim_mean = calculate_azimuthal_mean(data)
np.save("azim/ms_tem/t000.npy", azim_mean)  # 中間データ保存

# plot.py - 保存データを読み込み
data = np.load("azim/ms_tem/t000.npy")
plot(data)
```

#### After: オンデマンド計算
```python
# plot.py - 必要時に計算
data_tem = np.memmap("ms_tem.grd", ...)  # メモリマップ
data_pres = np.memmap("ms_pres.grd", ...)

theta = calculate_azimuthal_mean_theta(
    data_tem, data_pres, t, center_x, center_y, grid
)  # その場で計算
plot(theta)  # 直接プロット
```

### メモリマップの利点

```python
# 全データを読み込まない（メモリ効率的）
data = np.memmap(
    "ms_tem.grd",
    dtype=">f4",
    mode="r",
    shape=(nt, nz, ny, nx)
)

# 必要な時刻のみアクセス
data_t = data[t]  # 必要な時刻だけ読み込み
```

### 周期境界条件の処理

```python
# 領域端に近い台風を正確に扱う
dX = X - cx
dX[dX > 0.5 * x_width] -= x_width
dX[dX < -0.5 * x_width] += x_width

# 2つの距離を計算して最小値を採用
R = np.sqrt(dX**2 + dY**2)
R2 = np.sqrt(dX2**2 + dY2**2)
R = np.minimum(R, R2)
```

---

## Git履歴（直近12コミット）

| コミット | 内容 | 削減効果 |
|---------|------|---------|
| 965faf5 | 相対風の方位角平均をオンデマンド化 | 32%削減 |
| 721d75c | 温位・相当温位・角運動量計算をオンデマンド化 | 中間データ不要 |
| 3228883 | 温位・相当温位・角運動量プロットをオンデマンド化 | 中間データ不要 |
| 26637c7 | utils/azimuthal.pyに5関数追加 | 再利用性向上 |
| 8d62289 | 6つの風プロットをオンデマンド化 | 中間データ不要 |
| e7fbd40 | utils/azimuthal.py作成、2つのコアプロット移行 | 基盤整備 |
| 965fcad | vortex_regionのtheta_eプロットをオンデマンド化 | 3D中間データ不要 |
| 0fbaace | psi_plot_r200をvortex_regionに移動 | 実行順序最適化 |
| 94edafa | run_2dをbasicとwindに分割 | 依存関係明確化 |
| 7b860f8 | psi_plot_r200を3d_windに移動 | 依存関係明確化 |
| ... | ... | ... |

---

## 今後の展開

### 短期的タスク（1-2週間）

- [ ] 残りのazimuthal calcファイルのオンデマンド化
  - `azim_3d_calc.py`
  - `azim_wind_calc.py`
  - その他の*_calc.pyファイル

- [ ] 実行時間の計測
  - オンデマンド計算 vs 事前計算の比較
  - ボトルネック特定

- [ ] ドキュメントの整備
  - 各関数の使用例追加
  - MIGRATION_GUIDE.md更新

### 中期的タスク（1ヶ月）

- [ ] 他のカテゴリへの展開
  - symmetrisity/
  - z_profile/
  - 2d/

- [ ] パフォーマンス最適化
  - 並列処理の改善
  - キャッシュ機構の検討

- [ ] テストの追加
  - 単体テスト
  - 結果の妥当性検証

### 長期的展望（3ヶ月以上）

- [ ] 完全オンデマンド化
  - 全中間データの廃止検討
  - 計算時間との最適バランス

- [ ] データベース化
  - メタデータ管理
  - 実験管理システム

- [ ] WebUI開発
  - ブラウザベースの可視化
  - リアルタイムプロット

---

## まとめ

### 達成したこと

✅ **ストレージ大幅削減**: 1実験あたり~19GB、複数実験で最大~950GB削減
✅ **コードの統一化**: 重複ロジックを共通関数に集約
✅ **保守性向上**: 1箇所の修正で全体に反映
✅ **ドキュメント充実**: 全関数にdocstring追加
✅ **実行順序最適化**: 依存関係を明確化

### 技術的成果

- **メモリマップ活用**: 効率的な大容量データアクセス
- **周期境界処理**: 領域端の台風も正確に解析
- **関数ライブラリ**: 再利用可能な計算関数群
- **モジュール構造**: utils/配下の体系的整理

### プロジェクトの進化

このプロジェクトは、従来の「大量中間データ保存型」から「オンデマンド計算型」へと進化しました。この変更により、ストレージ容量の制約から解放され、より多くの実験ケースを扱えるようになりました。

同時に、コードの保守性が大幅に向上し、今後の機能追加や修正が容易になりました。

---

**作成日**: 2025-11-27
**作成者**: Claude Code
**プロジェクト**: tc_analyze
**バージョン**: 3.0 - オンデマンド計算最適化版
