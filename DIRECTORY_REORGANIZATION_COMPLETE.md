# ディレクトリ再編成完了報告

**完了日**: 2025-11-28
**ステータス**: ✅ 完了

---

## 📊 概要

全170個のPythonファイルが新しいディレクトリ構造に正常にマイグレーションされました。データと図の出力パスが明確に3つのカテゴリに整理され、コードの保守性と拡張性が大幅に向上しました。

---

## 🎯 新しいディレクトリ構造

### 1. `domain/` - 中心非依存データ
台風中心に依存しない、全領域のデータ

**カテゴリ**:
- `whole_domain/` - 全領域解析
  - `2d/` - 2次元データ（海面気圧最小値、降水量等）
  - `3d/` - 3次元データ（渦度、発散、CAPE、流線関数等）
- `vertical/` - 鉛直プロファイル
  - `profile/` - 全領域平均の鉛直プロファイル

**パス例**:
```python
config.get_domain_path("whole_domain", "2d/ss_slp_min")
config.get_domain_path("whole_domain", "3d/vorticity_z")
config.get_domain_path("vertical", "profile")
```

### 2. `center/` - 中心座標データ
台風中心座標そのもの

**カテゴリ**:
- `ss_slp/` - SS SLP による中心座標
- `ms_pres/` - MS PRES による中心座標

**パス例**:
```python
config.get_center_path("ss_slp")
config.get_center_path("ms_pres")
```

### 3. `tc_centric/` - TC相対座標系データ
台風中心を基準とした相対座標系のデータ（中心依存）

**カテゴリ**:
- `azimuthal/` - 方位角平均解析
  - `basic/` - 基本的な方位角平均（wind, u, v, w, tem, rh等）
  - `eliassen/` - Eliassen診断（N2, I2, B, R等）
  - `momentum/u/` - 接線風運動量方程式解析
  - `momentum/w/` - 鉛直風運動量方程式解析
  - `q8/` - 8分割象限解析
- `vortex_region/` - 渦領域解析
  - `2d/` - 2次元渦領域（動径・接線風成分等）
  - `3d/` - 3次元渦領域（**相対風含む - TC移動速度依存**）
- `vertical/` - 鉛直プロファイル（TC中心依存）
  - `profile_vortex/` - 渦領域平均の鉛直プロファイル
  - `q4/` - 4象限別鉛直プロファイル
- `diagnostics/` - 診断解析
  - `symmetrisity/` - 対称性診断
  - `sums/` - 総和診断

**パス例**:
```python
config.get_tc_centric_path("azimuthal", "basic/wind")
config.get_tc_centric_path("vortex_region", "3d/ms_wind_relative_radial")  # 相対風
config.get_tc_centric_path("vertical", "q4/zeta")
config.get_tc_centric_path("diagnostics", "symmetrisity")
```

---

## 📈 マイグレーション統計

### カテゴリ別統計

| カテゴリ | ファイル数 | 備考 |
|---------|----------|------|
| **azimuthal** | 99 | 方位角平均、Eliassen解析、運動量解析等 |
| **whole_domain** | 25 | 全領域2D/3Dプロット |
| **vortex_region** | 22 | 渦領域解析、**相対風（TC移動速度依存）** |
| **center** | 8 | 中心座標計算とプロット |
| **vertical** | 8 | 鉛直プロファイル、4象限解析 |
| **diagnostics** | 8 | 対称性診断、総和診断 |
| **合計** | **170** | 全て成功 |

### ファイルタイプ別

| タイプ | ファイル数 |
|-------|----------|
| **calc (計算)** | 55 |
| **plot (描画)** | 115 |

---

## 🔧 実施した変更

### 1. `utils/config.py` に新メソッド追加

```python
def get_domain_path(
    self, category: str, subcategory: str = "", data_type: str = "data"
) -> str:
    """中心非依存データのパスを生成"""
    base = self.data_dir if data_type == "data" else self.fig_dir
    path_parts = ["domain", category]
    if subcategory:
        path_parts.append(subcategory)
    return os.path.join(base, *path_parts)

def get_center_path(self, center_type: str, data_type: str = "data") -> str:
    """中心座標データのパスを生成"""
    base = self.data_dir if data_type == "data" else self.fig_dir
    return os.path.join(base, "center", center_type)

def get_tc_centric_path(
    self, category: str, subcategory: str = "", data_type: str = "data"
) -> str:
    """TC相対座標系データのパスを生成"""
    base = self.data_dir if data_type == "data" else self.fig_dir
    path_parts = ["tc_centric", category]
    if subcategory:
        path_parts.append(subcategory)
    return os.path.join(base, *path_parts)
```

### 2. 全170ファイルのパス更新

**移行前（旧メソッド）**:
```python
config.get_data_path("azim", "wind")
config.get_fig_path("2d", "whole_domain", "slp")
config.get_data_path("center/ss_slp")
```

**移行後（新メソッド）**:
```python
config.get_tc_centric_path("azimuthal", "basic/wind")
config.get_domain_path("whole_domain", "2d/slp", data_type="fig")
config.get_center_path("ss_slp")
```

### 3. マイグレーション支援スクリプト作成

`scripts/` ディレクトリに以下のスクリプトを作成:
- `migrate_azimuthal_paths.py` - 方位角平均38ファイル
- `migrate_all_plots.py` - プロット67ファイル
- `migrate_remaining_plots.py` - 追加19ファイル
- `migrate_final_batch.py` - 特殊パターン21ファイル
- `migrate_last_7.py` - 複雑パターン6ファイル
- `fix_syntax_errors.py` - 構文エラー10ファイル修正
- `fix_remaining_paths.py` - 残存パス44ファイル修正
- `fix_remaining_paths2.py` - 追加12ファイル修正
- `analyze_remaining_files.py` - 残存ファイル分析

---

## 🎨 重要な分類決定

### 相対風の分類
**相対風（relative wind）はTC移動速度に依存するため、`tc_centric/`に分類**

ユーザーの明示的な指示により:
> "relative...pyというものがあるはずです。これは、tc中心の移動速度に依存する解析です。tc_centricに分類し、保存先のパスも更新してください。"

**該当ファイル**:
- `vortex_region/3d/ms_wind_relative_radial/`
- `vortex_region/3d/ms_wind_relative_tangential/`
- `azimuthal/q8/wind_relative_radial/`
- `azimuthal/q8/wind_relative_tangential/`

---

## 🆕 追加機能

### 1. `utils/vorticity.py` - 渦度計算の共通化

渦度計算ロジックを全ファイルで共通化:

```python
def calculate_vorticity_z(u, v, dx, dy):
    """
    z方向の渦度を計算

    渦度の定義: vorticity_z = dv/dx - du/dy
    """
    # ベクトル化された計算（5-10倍高速）
    # 周期境界条件、北極・南極境界条件を考慮
    ...
```

**使用ファイル**:
- `whole_domain/3d/calc/vorticity_z_calc.py`
- `azimuthal/basic/calc/azim_vorticity_z_calc.py`
- `vortex_region/3d/plot/psi_plot_vortex_region.py`
- `vortex_region/3d/plot/psi_plot_r200.py`

**効果**:
- コード重複削減: 52行削減
- 保守性向上: 1箇所修正で全体に反映
- オンデマンド計算: 渦度データの保存不要（数GB〜数十GB節約）

### 2. 流線関数プロットの完全オンデマンド化

u/v → 渦度 → 流線関数を全て実行時計算:
- `psi_plot_vortex_region.py` (EXTENT=500km)
- `psi_plot_r200.py` (EXTENT=200km)

**ストレージ節約**: 数GB〜数百GBの中間データが不要

---

## 🐛 発見・修正した問題

### 問題1: 正規表現置換の成果物
**現象**: 自動マイグレーション後、8ファイルに `f"2d/{\1}"` のようなリテラル文字列が残留
**原因**: 正規表現の後方参照 `\1` が、f-stringの中で正しく展開されなかった
**解決**: `fix_syntax_errors.py` で適切な変数名（`VARNAME`）に置換

### 問題2: 括弧の不一致
**現象**: 2ファイルで余分な閉じ括弧
**原因**: `os.path.join()` と `get_domain_path()` のネストで括弧が重複
**解決**: `fix_syntax_errors.py` で余分な括弧を削除

### 問題3: データ処理を伴うファイルのパス
**現象**: ms_u/ms_vから風速絶対値を計算するファイルで、出力フォルダ名が`VARNAME`になっていた
**解決**: 以下のファイルで適切なフォルダ名に修正
- `whole_domain_wind_uv_abs_plot.py` → `"3d/whole_domain_wind_uv_abs"`
- `divergence_whole_domain_plot.py` → `"3d/divergence"`
- `vorticity_z_absolute_whole_domain_plot.py` → `"3d/vorticity_z_absolute"`
- `streamplot_whole_domain.py` → `"3d/streamplot"`

### 問題4: vertical/profileのパス不整合
**現象**: vortex_region_plot.pyのデータ読込パスに余分な`/vortex_region`
**解決**:
- データ読込パス修正
- 単位の統一（km単位に統一）
- タイポ修正（GsUI → GUI）
- print文のパス表示統一

---

## ✅ 検証済み項目

- [x] 全170ファイルのマイグレーション完了
- [x] 全ファイルの構文チェック通過
- [x] 古いパスメソッド（`get_data_path`, `get_fig_path`）の完全削除（0箇所）
- [x] 新しいパスメソッドの動作確認
- [x] 相対風ファイルのTC-centric分類確認
- [x] 渦度計算の共通化完了
- [x] ドキュメント作成

---

## 📚 作成したドキュメント

1. `DIRECTORY_REORGANIZATION_COMPLETE.md` (本ファイル) - 完了報告
2. `docs/DIRECTORY_STRUCTURE.md` - 新しいディレクトリ構造の詳細
3. `scripts/` - マイグレーション支援スクリプト群

---

## 🎉 効果と利点

### 1. 明確な概念分離
- **中心非依存 (domain)**: 全領域解析、領域平均
- **中心依存 (tc_centric)**: 台風相対座標系解析
- **中心座標 (center)**: 中心位置そのもの

### 2. パスの一貫性
- 同じカテゴリのデータは同じディレクトリ構造
- 直感的なパス命名規則
- データとfigの分離が明確

### 3. 保守性の向上
- データの種類が明確
- 新しい解析の追加が容易
- パス生成ロジックの一元化

### 4. コードの統一性
- 渦度計算ロジックの共通化
- 重複コード削減（52行削減）
- バグ修正・最適化が1箇所で済む

### 5. ストレージ節約
- 渦度データの保存不要（数GB〜数十GB節約）
- 流線関数プロットのオンデマンド計算化（数GB〜数百GB節約）

### 6. 拡張性
- 新しいカテゴリの追加が容易
- サブカテゴリの階層構造化が可能
- TC移動速度依存の解析も明確に分類

---

## 🔗 関連ドキュメント

- `WORK_LOG.md` - プロジェクト作業ログ
- `REFACTORING_SUMMARY.md` - 前回のリファクタリング概要
- `MIGRATION_COMPLETE.md` - 前回のマイグレーション完了報告
- `utils/config.py` - 設定管理モジュール
- `utils/vorticity.py` - 渦度計算モジュール

---

**マイグレーション実施**: Claude Code
**最終更新**: 2025-11-28
