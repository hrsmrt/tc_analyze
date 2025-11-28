# Directory Reorganization Proposal

**Date**: 2025-11-28
**Status**: Draft for Review

## 概要

データおよび図の出力ディレクトリを中心座標への依存性に基づいて3つのカテゴリに再編成します：

1. **domain** - 中心に依存しない領域全体のデータ/図
2. **center** - 中心座標データそのもの
3. **tc_centric** - 中心座標に依存するTC相対座標系でのデータ/図

---

## 新しいディレクトリ構造

### データディレクトリ (`./data/`)

```
data/
├── domain/                          # 中心に依存しないデータ
│   ├── whole_domain/
│   │   ├── 2d/
│   │   │   ├── ss_slp_min/         # 海面気圧最小値
│   │   │   └── ss_wind10m_max/     # 10m風速最大値
│   │   └── 3d/
│   │       ├── vorticity_z/        # 絶対渦度
│   │       └── divergence/         # 発散
│   └── vertical/
│       └── profile/                # 全領域平均鉛直プロファイル
│           ├── z_profile/          # 各変数のプロファイル
│           └── hf/                 # 湿潤静的エネルギー
│
├── center/                          # 中心座標データ
│   ├── ss_slp/                     # 海面気圧から求めた2D中心
│   └── ms_pres/                    # 3D気圧から求めた3D中心
│
└── tc_centric/                      # TC相対座標系データ（中心依存）
    ├── vortex_region/
    │   ├── 2d/
    │   │   └── ss_wind10m/         # 10m風の動径・接線成分
    │   └── 3d/
    │       ├── ms_wind/            # 風の動径・接線成分
    │       ├── ms_dyn/             # 力学テンダンシー成分
    │       ├── relative_wind/      # 相対風
    │       ├── vorticity_z/        # 渦度
    │       └── divergence/         # 発散
    │
    ├── azimuthal/                   # 方位角平均データ
    │   ├── basic/                   # 基本場
    │   │   ├── 2d/                 # 海面2D変数
    │   │   ├── 3d/                 # 3D変数の方位角平均
    │   │   ├── wind/               # 風場（動径・接線成分）
    │   │   ├── wind_relative/      # 相対風
    │   │   ├── wind10m/            # 10m風
    │   │   ├── vorticity_z/        # 渦度
    │   │   ├── theta/              # 温位
    │   │   ├── theta_e/            # 相当温位
    │   │   ├── momentum/           # 運動量
    │   │   ├── stream/             # 流線関数
    │   │   ├── pert_3d/            # 擾乱成分
    │   │   ├── dyn/                # 力学テンダンシー
    │   │   ├── mp/                 # 雲微物理テンダンシー
    │   │   ├── phy/                # 物理過程テンダンシー
    │   │   └── tb/                 # 乱流テンダンシー
    │   │
    │   ├── eliassen/                # エリアッセン診断関連
    │   │   ├── N2/                 # 浮力振動数の2乗
    │   │   ├── I2/                 # 慣性安定度の2乗
    │   │   ├── I_prime2/           # 修正慣性安定度の2乗
    │   │   ├── B/                  # B係数
    │   │   ├── R/                  # R係数
    │   │   ├── gamma/              # γ係数
    │   │   ├── xi/                 # ξ係数
    │   │   └── buoyancy/           # 浮力
    │   │
    │   ├── momentum/                # 運動量方程式診断
    │   │   ├── u/                  # 接線風運動量方程式
    │   │   │   ├── du_dr/          # 動径微分
    │   │   │   ├── du_dz/          # 鉛直微分
    │   │   │   ├── udu_dr/         # 移流項（動径）
    │   │   │   ├── wdu_dz/         # 移流項（鉛直）
    │   │   │   ├── grad_p/         # 気圧傾度力
    │   │   │   ├── coriolis/       # コリオリ力
    │   │   │   ├── centrifugal/    # 遠心力
    │   │   │   ├── gradient_wind_eq/      # 傾度風平衡
    │   │   │   └── gradient_balance_score/ # 傾度風平衡スコア
    │   │   └── w/                  # 鉛直風運動量方程式
    │   │       ├── wdw_dz/         # 移流項
    │   │       └── grad_p/         # 気圧傾度力
    │   │
    │   └── q8/                      # 8方位分割データ
    │       ├── 3d/                 # 3D変数の8方位平均
    │       └── wind_relative/      # 相対風の8方位平均
    │
    ├── vertical/
    │   ├── profile_vortex/          # 渦領域平均鉛直プロファイル
    │   │   └── vortex_region/      # R<=500km領域の平均
    │   └── q4/                      # 4象限別鉛直プロファイル
    │       └── zeta/               # 渦度の4象限プロファイル
    │
    └── diagnostics/                 # 診断量
        ├── sums/                    # TC周辺領域の総和
        └── symmetrisity/            # 軸対称性指標
            ├── 3d/                 # 3D変数の軸対称性
            └── wind_relative/      # 相対風の軸対称性
```

### 図ディレクトリ (`./fig/`)

図ディレクトリもデータディレクトリと同じ構造に従います：

```
fig/
├── domain/
│   ├── whole_domain/
│   │   ├── 2d/
│   │   └── 3d/
│   └── vertical/
│       └── profile/
│
├── center/
│   ├── ss_slp/
│   └── ms_pres/
│
└── tc_centric/
    ├── vortex_region/
    ├── azimuthal/
    ├── vertical/
    └── diagnostics/
```

---

## 分類の詳細

### 1. Domain（中心非依存）

#### 判定基準
- 中心座標 (`center_x`, `center_y`) を使用しない
- 全領域の平均または全領域での探索を行う
- `.mean(axis=(2,3))` や `.mean(axis=(1,2))` を使用

#### 該当ファイル

**whole_domain/2d/** (2ファイル)
- `ss_slp_min_calc.py` - 全領域で最小海面気圧を探索
- `ss_wind10m_max_calc.py` - 全領域で最大10m風速を探索

**whole_domain/3d/** (2ファイル)
- `vorticity_z_calc.py` - 全領域の絶対渦度
- `divergence_calc.py` - 全領域の発散

**vertical/profile/** (2ファイル)
- `z_profile_calc.py` - 全領域平均の鉛直プロファイル（`.mean(axis=(2,3))`）
- `hf_calc.py` - 全領域平均の湿潤静的エネルギー（`.mean(axis=(1,2))`）

**プロットファイル**: 対応する calc ファイルのプロット

---

### 2. Center（中心座標データ）

#### 判定基準
- 中心座標そのものを計算・管理するファイル

#### 該当ファイル

**center/** (2ファイル)
- `ss_slp_center_calc.py` - 海面気圧から2D中心を計算
- `ms_pres_center_calc.py` - 3D気圧から3D中心を計算

**プロットファイル**: 中心軌跡のプロット

---

### 3. TC-Centric（中心依存）

#### 判定基準
- 中心座標 (`center_x`, `center_y`) を使用
- TC相対座標系（動径・接線、方位角）での解析
- 中心からの距離 `R` を計算

#### 該当ファイル（カテゴリ別）

**vortex_region/2d/** (1ファイル)
- `ss_wind10m_radial_tangential_calc.py` - 10m風をTC相対座標に変換

**vortex_region/3d/** (1ファイル)
- `ms_dyn_radial_tangential_calc.py` - 力学テンダンシーをTC相対座標に変換

**azimuthal/basic/** (17ファイル)
- `azim_2d_calc.py` - 2D変数の方位角平均
- `azim_3d_calc.py` - 3D変数の方位角平均
- `azim_wind_calc.py` - 風場の方位角平均
- `azim_wind_relative_calc.py` - 相対風の方位角平均
- `azim_wind10m_calc.py` - 10m風の方位角平均
- `azim_vorticity_z_calc.py` - 渦度の方位角平均
- `azim_theta_calc.py` - 温位の方位角平均
- `azim_theta_e_calc.py` - 相当温位の方位角平均
- `azim_momentum_calc.py` - 運動量の方位角平均
- `azim_stream_calc.py` - 流線関数の方位角平均
- `azim_stream2_calc.py` - 流線関数の方位角平均（別バージョン）
- `azim_pert_3d_calc.py` - 擾乱成分の方位角平均
- `azim_dyn_calc.py` - 力学テンダンシーの方位角平均
- `azim_mp_calc.py` - 雲微物理テンダンシーの方位角平均
- `azim_phy_calc.py` - 物理過程テンダンシーの方位角平均
- `azim_tb_calc.py` - 乱流テンダンシーの方位角平均
- `azim_wind10m_tangential_max_calc.py` - 10m接線風の最大値

**azimuthal/eliassen/** (8ファイル)
- `azim_N2_calc.py` - 浮力振動数の2乗
- `azim_I2_calc.py` - 慣性安定度の2乗
- `azim_I_prime2_calc.py` - 修正慣性安定度の2乗
- `azim_B_calc.py` - B係数
- `azim_R_calc.py` - R係数
- `azim_gamma_calc.py` - γ係数
- `azim_xi_calc.py` - ξ係数
- `azim_buoyancy_calc.py` - 浮力

**azimuthal/momentum/u/** (9ファイル)
- `azim_du_dr_calc.py` - 接線風の動径微分
- `azim_du_dz_calc.py` - 接線風の鉛直微分
- `azim_udu_dr_calc.py` - 移流項（動径）
- `azim_wdu_dz_calc.py` - 移流項（鉛直）
- `azim_grad_p_calc.py` - 気圧傾度力
- `azim_coriolis_calc.py` - コリオリ力
- `azim_centrifugal_calc.py` - 遠心力
- `azim_gradient_wind_eq_calc.py` - 傾度風平衡
- `azim_gradient_balance_score_calc.py` - 傾度風平衡スコア

**azimuthal/momentum/w/** (2ファイル)
- `azim_wdw_dz_calc.py` - 鉛直移流項
- `azim_grad_p_calc.py` - 気圧傾度力

**azimuthal/q8/** (2ファイル)
- `azim_q8_3d_calc.py` - 3D変数の8方位平均
- `azim_q8_wind_relative_calc.py` - 相対風の8方位平均

**vertical/profile_vortex/** (1ファイル)
- `vortex_region_calc.py` - 渦領域（R<=500km）平均の鉛直プロファイル

**vertical/q4/** (1ファイル)
- `vorticity_z_calc.py` - 4象限別の渦度鉛直プロファイル

**diagnostics/sums/** (1ファイル)
- `sums_calc.py` - TC中心周辺領域の変数総和

**diagnostics/symmetrisity/** (3ファイル)
- `3d_calc.py` - 3D変数の軸対称性指標
- `relative_wind_radial_calc.py` - 相対風動径成分の軸対称性
- `relative_wind_tangential_calc.py` - 相対風接線成分の軸対称性

**プロットファイル**: 各カテゴリに対応する多数のプロットファイル

---

## 統計

### ファイル数サマリー

| カテゴリ | calcファイル | plotファイル | 合計 |
|---------|-------------|-------------|------|
| **Domain** | 4 | ~10 | ~14 |
| **Center** | 2 | ~3 | ~5 |
| **TC-Centric** | 46 | ~110 | ~156 |
| **合計** | 52 | ~123 | ~175 |

### ディレクトリ分類

```
domain/
  whole_domain/
    2d/          - 2 calc, ~4 plot
    3d/          - 2 calc, ~6 plot
  vertical/
    profile/     - 2 calc, ~3 plot

center/
  ss_slp/        - 1 calc, ~2 plot
  ms_pres/       - 1 calc, ~1 plot

tc_centric/
  vortex_region/
    2d/          - 1 calc, ~3 plot
    3d/          - 1 calc, ~10 plot
  azimuthal/
    basic/       - 17 calc, ~52 plot
    eliassen/    - 8 calc, ~8 plot
    momentum/u/  - 9 calc, ~9 plot
    momentum/w/  - 2 calc, ~2 plot
    q8/          - 2 calc, ~3 plot
  vertical/
    profile_vortex/ - 1 calc, ~1 plot
    q4/          - 1 calc, ~1 plot
  diagnostics/
    sums/        - 1 calc, ~1 plot
    symmetrisity/ - 3 calc, ~3 plot
```

---

## 実装計画

### 1. utils/config.py への追加

新しいパス生成メソッドを追加：

```python
def get_domain_path(self, category: str, subcategory: str = "", data_type: str = "data") -> str:
    """中心非依存データのパスを生成

    Args:
        category: whole_domain, vertical など
        subcategory: 2d, 3d, profile など
        data_type: "data" または "fig"

    Returns:
        パス文字列（例: "./data/domain/whole_domain/2d"）
    """
    base = self.data_dir if data_type == "data" else self.fig_dir
    path_parts = ["domain", category]
    if subcategory:
        path_parts.append(subcategory)
    return os.path.join(base, *path_parts)

def get_center_path(self, center_type: str, data_type: str = "data") -> str:
    """中心座標データのパスを生成

    Args:
        center_type: "ss_slp" または "ms_pres"
        data_type: "data" または "fig"

    Returns:
        パス文字列（例: "./data/center/ss_slp"）
    """
    base = self.data_dir if data_type == "data" else self.fig_dir
    return os.path.join(base, "center", center_type)

def get_tc_centric_path(self, category: str, subcategory: str = "", data_type: str = "data") -> str:
    """TC相対座標系データのパスを生成

    Args:
        category: vortex_region, azimuthal, vertical, diagnostics など
        subcategory: basic, eliassen, momentum/u など（階層的に指定可能）
        data_type: "data" または "fig"

    Returns:
        パス文字列（例: "./data/tc_centric/azimuthal/basic"）
    """
    base = self.data_dir if data_type == "data" else self.fig_dir
    path_parts = ["tc_centric", category]
    if subcategory:
        path_parts.append(subcategory)
    return os.path.join(base, *path_parts)
```

### 2. 段階的移行手順

#### Phase 1: utils/config.py の更新
1. 新しいパス生成メソッドを追加
2. 既存の `get_data_path()` メソッドは後方互換性のため維持

#### Phase 2: ファイル別の移行（優先順位）
1. **Center** (2 calc + plot) - 最も影響範囲が小さい
2. **Domain** (4 calc + plot) - 影響範囲小
3. **TC-Centric** (46 calc + plot) - 段階的に移行
   - vortex_region/ から開始
   - azimuthal/basic/
   - azimuthal/eliassen/
   - azimuthal/momentum/
   - その他

#### Phase 3: 動作確認
各フェーズ後に以下を実施：
- 構文チェック: `python -m py_compile`
- サンプル実行テスト
- 出力ファイルの確認

#### Phase 4: ドキュメント更新
- README.md の更新
- 新しいディレクトリ構造の説明文書作成

---

## 移行例

### Before（現状）
```python
# analysis/whole_domain/2d/calc/ss_slp_min_calc.py
output_dir = config.get_data_path("2d", "ss_slp_min")
os.makedirs(output_dir, exist_ok=True)
```

### After（移行後）
```python
# analysis/whole_domain/2d/calc/ss_slp_min_calc.py
output_dir = config.get_domain_path("whole_domain", "2d/ss_slp_min")
os.makedirs(output_dir, exist_ok=True)
```

### Before（現状）
```python
# analysis/azimuthal/basic/calc/azim_wind_calc.py
output_folder = config.get_data_path("azim", "wind")
os.makedirs(output_folder, exist_ok=True)
```

### After（移行後）
```python
# analysis/azimuthal/basic/calc/azim_wind_calc.py
output_folder = config.get_tc_centric_path("azimuthal", "basic/wind")
os.makedirs(output_folder, exist_ok=True)
```

### Before（現状）
```python
# analysis/center/calc/ss_slp_center_calc.py
OUTPUT_DIR = config.get_data_path("center/ss_slp")
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

### After（移行後）
```python
# analysis/center/calc/ss_slp_center_calc.py
OUTPUT_DIR = config.get_center_path("ss_slp")
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

---

## 既存データの移行

既存のデータディレクトリを新しい構造に移行するシェルスクリプトを作成します：

```bash
#!/bin/bash
# scripts/migrate_data_structure.sh

# Domainカテゴリ
mkdir -p data/domain/whole_domain/{2d,3d}
mkdir -p data/domain/vertical/profile
mv data/2d/ss_slp_min data/domain/whole_domain/2d/
mv data/2d/ss_wind10m_max data/domain/whole_domain/2d/
mv data/3d/vorticity_z data/domain/whole_domain/3d/
mv data/3d/divergence data/domain/whole_domain/3d/
mv data/z_profile data/domain/vertical/profile/

# Centerカテゴリ
mkdir -p data/center/{ss_slp,ms_pres}
mv data/center/ss_slp/* data/center/ss_slp/ 2>/dev/null || true
mv data/center/ms_pres/* data/center/ms_pres/ 2>/dev/null || true

# TC-Centricカテゴリ
mkdir -p data/tc_centric/vortex_region/{2d,3d}
mkdir -p data/tc_centric/azimuthal/{basic,eliassen,momentum,q8}
mkdir -p data/tc_centric/vertical/{profile_vortex,q4}
mkdir -p data/tc_centric/diagnostics/{sums,symmetrisity}

# ... その他の移動コマンド ...

echo "Migration complete!"
```

---

## 確認事項

以下の点についてご確認ください：

1. **ディレクトリ構造**: 提案した3層構造（domain/center/tc_centric）は適切ですか？
2. **サブディレクトリ名**: 各サブディレクトリの命名は分かりやすいですか？
3. **分類の正確性**: 各ファイルの分類（domain/center/tc_centric）は正しいですか？
4. **移行の優先順位**: 提案した段階的移行手順は適切ですか？
5. **その他**: 追加の考慮事項や変更希望はありますか？

---

## 次のステップ

承認後、以下の順序で実装を進めます：

1. ✅ この提案書のレビューと承認
2. ⬜ `utils/config.py` への新メソッド追加
3. ⬜ Center カテゴリファイルの移行（2 calc + plot）
4. ⬜ Domain カテゴリファイルの移行（4 calc + plot）
5. ⬜ TC-Centric カテゴリファイルの段階的移行（46 calc + plot）
6. ⬜ 既存データ移行スクリプトの作成と実行
7. ⬜ ドキュメントの更新

---

**この提案書をご確認いただき、承認または修正のご指示をお願いします。**
