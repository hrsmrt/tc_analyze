# ディレクトリ構造

**最終更新**: 2025-11-28

## 概要

データおよび図の出力ディレクトリは、中心座標への依存性に基づいて3つのカテゴリに分類されています：

1. **domain/** - 中心座標に依存しない全領域データ
2. **center/** - 中心座標データそのもの
3. **tc_centric/** - TC相対座標系データ（中心座標依存）

---

## data/ および fig/ の構造

```
data/ (または fig/)
├── domain/                          # 中心非依存
│   ├── whole_domain/
│   │   ├── 2d/
│   │   │   ├── ss_slp_min/         # 海面気圧最小値
│   │   │   └── ss_wind10m_max/     # 10m風速最大値
│   │   └── 3d/
│   │       ├── vorticity_z/        # 絶対渦度
│   │       └── divergence/         # 発散
│   └── vertical/
│       └── profile/                # 全領域平均鉛直プロファイル
│
├── center/                          # 中心座標データ
│   ├── ss_slp/                     # 海面気圧から求めた2D中心
│   └── ms_pres/                    # 3D気圧から求めた3D中心
│
└── tc_centric/                      # TC相対座標系データ
    ├── vortex_region/               # 渦領域のTC相対データ
    │   ├── 2d/
    │   │   ├── ss_wind10m_radial/
    │   │   └── ss_wind10m_tangential/
    │   └── 3d/
    │       ├── ms_dyn_radial/
    │       └── ms_dyn_tangential/
    │
    ├── azimuthal/                   # 方位角平均データ
    │   ├── basic/                   # 基本場
    │   │   ├── wind_radial/
    │   │   ├── wind_tangential/
    │   │   ├── wind_relative_radial/
    │   │   ├── wind_relative_tangential/
    │   │   ├── theta/
    │   │   ├── theta_e/
    │   │   └── ...
    │   ├── eliassen/                # エリアッセン診断
    │   │   ├── N2/
    │   │   ├── I2/
    │   │   ├── B/
    │   │   └── ...
    │   ├── momentum/                # 運動量方程式診断
    │   │   ├── u/
    │   │   └── w/
    │   └── q8/                      # 8方位分割
    │
    ├── vertical/                    # TC中心基準の鉛直プロファイル
    │   ├── profile_vortex/          # 渦領域平均（R<=500km）
    │   └── q4/                      # 4象限別
    │
    └── diagnostics/                 # 診断量
        ├── sums/                    # TC周辺領域の総和
        └── symmetrisity/            # 軸対称性指標
```

---

## カテゴリの詳細

### 1. Domain（中心非依存）

**特徴**:
- 中心座標（`center_x`, `center_y`）を使用しない
- 全領域の平均または全領域での探索を行う

**含まれるデータ**:
- 全領域での最小海面気圧・最大10m風速
- 全領域の絶対渦度・発散
- 全領域平均の鉛直プロファイル

**パス生成**:
```python
config.get_domain_path("whole_domain", "2d/ss_slp_min")
config.get_domain_path("vertical", "profile")
```

### 2. Center（中心座標データ）

**特徴**:
- 中心座標そのものを計算・保存

**含まれるデータ**:
- SS SLP: 海面気圧から求めた2D中心座標（形状: nt, 2）
- MS PRES: 3D気圧から求めた3D中心座標（形状: nt, nz, 2）

**パス生成**:
```python
config.get_center_path("ss_slp")
config.get_center_path("ms_pres")
```

### 3. TC-Centric（TC相対座標系データ）

**特徴**:
- 中心座標を使用してTC相対座標系で解析
- 動径・接線成分、方位角平均など

**含まれるデータ**:
- **vortex_region/**: 渦領域のTC相対データ
- **azimuthal/**: 方位角平均データ（基本場、診断量）
- **vertical/**: TC中心基準の鉛直プロファイル
- **diagnostics/**: 軸対称性指標、総和など

**パス生成**:
```python
config.get_tc_centric_path("vortex_region", "2d/ss_wind10m_radial")
config.get_tc_centric_path("azimuthal", "basic/wind")
config.get_tc_centric_path("azimuthal", "momentum/u/grad_p")
config.get_tc_centric_path("diagnostics", "sums")
```

---

## パス生成メソッド

### get_domain_path()

中心非依存データのパス生成

```python
def get_domain_path(category: str, subcategory: str = "", data_type: str = "data") -> str
```

**引数**:
- `category`: カテゴリ名（whole_domain, vertical など）
- `subcategory`: サブカテゴリ（2d, 3d, profile など）
- `data_type`: "data" または "fig"

**例**:
```python
config.get_domain_path("whole_domain", "2d/ss_slp_min")
# → "./data/domain/whole_domain/2d/ss_slp_min"

config.get_domain_path("vertical", "profile", data_type="fig")
# → "./fig/domain/vertical/profile"
```

### get_center_path()

中心座標データのパス生成

```python
def get_center_path(center_type: str, data_type: str = "data") -> str
```

**引数**:
- `center_type`: "ss_slp" または "ms_pres"
- `data_type`: "data" または "fig"

**例**:
```python
config.get_center_path("ss_slp")
# → "./data/center/ss_slp"
```

### get_tc_centric_path()

TC相対座標系データのパス生成

```python
def get_tc_centric_path(category: str, subcategory: str = "", data_type: str = "data") -> str
```

**引数**:
- `category`: カテゴリ名（vortex_region, azimuthal, vertical, diagnostics など）
- `subcategory`: サブカテゴリ（階層的に指定可能）
- `data_type`: "data" または "fig"

**例**:
```python
config.get_tc_centric_path("azimuthal", "basic/wind")
# → "./data/tc_centric/azimuthal/basic/wind"

config.get_tc_centric_path("azimuthal", "momentum/u/grad_p")
# → "./data/tc_centric/azimuthal/momentum/u/grad_p"
```

---

## 移行履歴

**v2.3.0** (2025-11-28):
- 全54個のcalcファイルを新しいディレクトリ構造に移行
- `utils/config.py` に新しいパス生成メソッドを追加
- domain/center/tc_centric の3層構造を導入

---

## 関連ドキュメント

- `DIRECTORY_REORGANIZATION_PROPOSAL.md` - 詳細な提案書と分類根拠
- `docs/CENTER_CONFIGURATION.md` - 中心座標の設定方法
- `docs/COMMAND_REFERENCE.md` - CLIコマンドリファレンス
