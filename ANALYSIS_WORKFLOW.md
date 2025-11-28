# TC解析ワークフロー

**最終更新**: 2025-11-28

このドキュメントでは、TC解析の標準的な実行フローを説明します。

---

## 📋 解析フロー概要

```
1. 準備
   ↓
2. 並列実行可能（中心位置非依存）
   ├─ TC中心位置の特定
   ├─ 時系列解析（極値・最大風速等）
   └─ 全領域分布の描画
   ↓
3. TC中心依存解析
   ├─ 渦領域解析
   └─ 方位角平均解析
```

---

## 1️⃣ 準備

### 必要なファイル

#### 1.1 設定ファイル: `setting.json`

作業ディレクトリに配置します（サンプル: `run/setting.json`）。

```json
{
  "nt": 101,
  "t_first": 0,
  "t_last": 100,
  "triangle_size": 256000.0,
  "glevel": 7,
  "nz": 74,
  "dt_output": 86400,
  "n_jobs": 4,
  "input_folder": "../convert/",
  "vgrid_filepath": "/path/to/vgrid_c74.txt",
  "data_dir": "./data",
  "fig_dir": "./fig"
}
```

詳細は[README.md](./README.md)の「設定項目の説明」を参照。

#### 1.2 変数リスト: `filenames_2d.txt`, `filenames_3d.txt`

プロット対象の変数を記載します（サンプル: `run/filenames_2d.txt`, `run/filenames_3d.txt`）。

**`filenames_2d.txt` の例**:
```
ss_slp
ss_tppn
ss_u10m
ss_v10m
ss_t2m
```

**`filenames_3d.txt` の例**:
```
ms_u
ms_v
ms_w
ms_tem
ms_qv
ms_pres
```

---

## 2️⃣ 並列実行可能な解析（中心位置非依存）

この段階の解析は**TC中心位置に依存しない**ため、**任意の順序または並列で実行可能**です。

### 2.1 TC中心位置の特定

**目的**: TC中心座標を計算し、以降の解析で使用

**実行方法**:
```bash
# 海面気圧（SLP）による2次元中心検出
sh $WORK/tc_analyze/run/analyze.sh center

# または、3次元圧力データによる中心検出
python $WORK/tc_analyze/analysis/center/ms_pres/calc/ms_pres_center_calc.py
```

**出力**:
- `data/center/ss_slp/center.npz` - 2次元中心座標 (shape: nt×2)
- `data/center/ms_pres/center.npz` - 3次元中心座標 (shape: nt×nz×2)

**次に進む条件**: このステップが完了すると、中心依存解析（ステップ3）が実行可能になります。

---

### 2.2 時系列解析（極値・最大風速等）

**目的**: 気圧極小値、最大風速、降水量などの時間変化を描画

**実行方法**:
```bash
# 海面気圧の最小値
python $WORK/tc_analyze/analysis/whole_domain/2d/calc/ss_slp_min_calc.py
python $WORK/tc_analyze/analysis/whole_domain/2d/plot/ss_slp_min_plot.py

# 降水量の時系列（領域積算）
python $WORK/tc_analyze/analysis/whole_domain/2d/calc/ss_tppn_sum_calc.py
python $WORK/tc_analyze/analysis/whole_domain/2d/plot/ss_tppn_sum_plot.py
```

**出力**:
- `data/domain/whole_domain/2d/ss_slp_min/` - 最小値データ
- `fig/domain/whole_domain/2d/ss_slp_min/` - 時系列プロット

**カテゴリ**: `domain/whole_domain/2d/` - 中心非依存データ

---

### 2.3 全領域分布の描画

**目的**: 変数の空間分布を全領域で可視化

**実行方法**:
```bash
# 2次元データ（例: 海面気圧）
python $WORK/tc_analyze/analysis/whole_domain/2d/plot/whole_domain.py ss_slp

# 3次元データ（例: 水平風）
python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain.py ms_u
python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain.py ms_v

# 複数変数を一括実行（シェルループ）
while read varname; do
    python $WORK/tc_analyze/analysis/whole_domain/2d/plot/whole_domain.py $varname
done < filenames_2d.txt
```

**出力**:
- `fig/domain/whole_domain/2d/{varname}/` - 2次元分布図
- `fig/domain/whole_domain/3d/{varname}/` - 3次元分布図（高度別）

**カテゴリ**: `domain/whole_domain/` - 中心非依存データ

---

## 3️⃣ TC中心依存解析

この段階の解析は**TC中心座標が必要**なため、**ステップ2.1の完了後**に実行します。

### 前提条件

✅ TC中心座標ファイルが存在すること:
- `data/center/ss_slp/center.npz` (2次元中心)
- または `data/center/ms_pres/center.npz` (3次元中心)

---

### 3.1 渦領域解析

**目的**: TC中心を基準とした相対座標系でデータを解析

**実行方法**:
```bash
# 渦領域の動径風・接線風成分を計算
sh $WORK/tc_analyze/run/analyze.sh vortex_region

# または個別に実行
python $WORK/tc_analyze/analysis/vortex_region/3d/calc/ms_wind_radial_tangential_calc.py
python $WORK/tc_analyze/analysis/vortex_region/3d/plot/ms_wind_radial_plot.py
python $WORK/tc_analyze/analysis/vortex_region/3d/plot/ms_wind_tangential_plot.py
```

**出力**:
- `data/tc_centric/vortex_region/3d/ms_wind_radial/` - 動径風成分
- `data/tc_centric/vortex_region/3d/ms_wind_tangential/` - 接線風成分
- `fig/tc_centric/vortex_region/3d/` - 渦領域の分布図

**カテゴリ**: `tc_centric/vortex_region/` - TC相対座標系データ

---

### 3.2 方位角平均解析

**目的**: TC中心からの距離と高度の2次元断面で変数を平均化

**実行方法**:
```bash
# 方位角平均の基本解析
sh $WORK/tc_analyze/run/analyze.sh azim

# Eliassen診断
sh $WORK/tc_analyze/run/analyze.sh azim_eliassen

# 運動量方程式解析
sh $WORK/tc_analyze/run/analyze.sh azim_eq_momentum_u
sh $WORK/tc_analyze/run/analyze.sh azim_eq_momentum_w

# 8方位分割解析
sh $WORK/tc_analyze/run/analyze.sh azim_q8
```

**出力**:
- `data/tc_centric/azimuthal/basic/` - 基本的な方位角平均
- `data/tc_centric/azimuthal/eliassen/` - Eliassen診断
- `data/tc_centric/azimuthal/momentum/` - 運動量方程式項
- `fig/tc_centric/azimuthal/` - 方位角平均の断面図

**カテゴリ**: `tc_centric/azimuthal/` - TC相対座標系データ

---

## 🔄 完全な実行例

### 最小限のワークフロー（中心検出 → 方位角平均）

```bash
# 作業ディレクトリに移動
cd /path/to/workdir

# 1. TC中心位置を計算
sh $WORK/tc_analyze/run/analyze.sh center

# 2. 方位角平均を計算・描画
sh $WORK/tc_analyze/run/analyze.sh azim
```

---

### 全解析の実行

```bash
# 作業ディレクトリに移動
cd /path/to/workdir

# オプション1: 全てを順次実行（推奨）
sh $WORK/tc_analyze/run/analyze.sh all

# オプション2: 段階的に実行
# ステップ2: 中心非依存解析（並列実行可能）
sh $WORK/tc_analyze/run/analyze.sh center &
sh $WORK/tc_analyze/run/analyze.sh 2d &
sh $WORK/tc_analyze/run/analyze.sh 3d_basic &
wait  # 全ての並列処理を待つ

# ステップ3: 中心依存解析
sh $WORK/tc_analyze/run/analyze.sh vortex_region
sh $WORK/tc_analyze/run/analyze.sh azim
sh $WORK/tc_analyze/run/analyze.sh azim_eliassen
```

---

## 📂 データ出力ディレクトリ構造

解析結果は以下の3つのカテゴリに分類されます：

### 1. `domain/` - 中心非依存データ
```
data/domain/
├── whole_domain/
│   ├── 2d/
│   │   ├── ss_slp_min/      # 海面気圧最小値
│   │   ├── ss_tppn_sum/     # 降水量積算
│   │   └── ...
│   └── 3d/
│       ├── vorticity_z/     # 渦度
│       ├── divergence/      # 発散
│       └── ...
└── vertical/
    └── profile/             # 全領域鉛直プロファイル
```

### 2. `center/` - 中心座標データ
```
data/center/
├── ss_slp/
│   └── center.npz          # 海面気圧による中心座標
└── ms_pres/
    └── center.npz          # 3次元圧力による中心座標
```

### 3. `tc_centric/` - TC相対座標系データ
```
data/tc_centric/
├── azimuthal/
│   ├── basic/              # 基本的な方位角平均（wind, u, v, w等）
│   ├── eliassen/           # Eliassen診断（N2, I2, B等）
│   ├── momentum/           # 運動量方程式解析
│   └── q8/                 # 8方位分割解析
├── vortex_region/
│   ├── 2d/                 # 渦領域2次元解析
│   └── 3d/                 # 渦領域3次元解析
├── vertical/
│   ├── profile_vortex/     # 渦領域鉛直プロファイル
│   └── q4/                 # 4象限鉛直プロファイル
└── diagnostics/
    ├── symmetrisity/       # 対称性診断
    └── sums/               # 積算診断
```

詳細は`DIRECTORY_REORGANIZATION_COMPLETE.md`を参照。

---

## 🛠️ トラブルシューティング

### Q1: 「中心座標ファイルが見つかりません」エラー

**原因**: ステップ2.1（中心位置の特定）が未実行

**解決策**:
```bash
sh $WORK/tc_analyze/run/analyze.sh center
```

### Q2: 並列実行時にメモリ不足

**原因**: `n_jobs`が大きすぎる

**解決策**: `setting.json`の`n_jobs`を減らす
```json
{
  "n_jobs": 2
}
```

### Q3: 特定の変数のみプロットしたい

**解決策**: Pythonスクリプトを直接実行
```bash
# 1つだけ
python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain.py ms_u

# 複数指定
for var in ms_u ms_v ms_tem; do
    python $WORK/tc_analyze/analysis/whole_domain/3d/plot/whole_domain.py $var
done
```

---

## 📚 関連ドキュメント

- [README.md](./README.md) - プロジェクト概要、環境構築、クイックスタート
- [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) - コマンドリファレンス、よく使うコマンド
- [WORK_LOG.md](./WORK_LOG.md) - コーディング規約、確立されたパターン
- [DIRECTORY_REORGANIZATION_COMPLETE.md](./DIRECTORY_REORGANIZATION_COMPLETE.md) - ディレクトリ構造の詳細
- [docs/CENTER_CONFIGURATION.md](./docs/CENTER_CONFIGURATION.md) - 中心座標の設定・計算方法

---

**作成日**: 2025-11-28
