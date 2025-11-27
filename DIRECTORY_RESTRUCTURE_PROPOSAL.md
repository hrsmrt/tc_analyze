# ディレクトリ構造再編提案

## 📊 現状分析

### 現在のディレクトリ構造

```
tc_analyze/
├── 2d/                (16 .py: 3 calc, 6 plot)
├── 3d/                (37 .py: 8 calc, 20 plot)
├── azim_mean/         (56 .py: 17 calc, 35 plot)
│   ├── eliassen/      (16 .py)
│   ├── eq_momentum_u/ (18 .py)
│   └── eq_momentum_w/ (4 .py)
├── azim_q8/           (5 .py: 2 calc, 3 plot)
├── center/            (8 .py: 1 calc, 1 plot)
├── sums/              (2 .py: 1 calc, 1 plot)
├── symmetrisity/      (6 .py: 3 calc, 3 plot)
├── z_profile/         (7 .py: 3 calc, 3 plot)
├── z_profile_q4/      (2 .py: 1 calc, 1 plot)
├── utils/             (8 .py: 共通モジュール)
├── script/            (4 .sh)
├── scripts/           (4 .py) ⚠️
├── data_processing/   (8 .py, 2 .sh)
├── examples/          (3 .py)
├── specific/          (2 .py)
└── sample/            (空) ⚠️

合計: 164 Python files (41 calc, 76 plot)
```

### 統計サマリー

| カテゴリ | ファイル数 | calc | plot | 備考 |
|---------|----------|------|------|------|
| 3d | 37 | 8 | 20 | 最大 |
| azim_mean | 56 + 38サブ | 17 | 35 | サブディレクトリあり |
| 2d | 16 | 3 | 6 | |
| その他 | 55 | 13 | 15 | 分散 |

---

## ⚠️ 現状の問題点

### 1. **calc/plot の混在**
- **問題**: ほぼ全てのディレクトリで計算スクリプト（calc）と可視化スクリプト（plot）が混在
- **影響**:
  - データフローが不明確
  - メンテナンス性が低い
  - スクリプト数が多いディレクトリ（azim_mean: 56ファイル）が見づらい

### 2. **ディレクトリ命名の不一致**
- **問題**: カテゴリ名とディレクトリ名が一致しない
  - カテゴリ `azim` ≠ ディレクトリ `azim_mean/`
  - カテゴリ `azim_eliassen` = ディレクトリ `azim_mean/eliassen/`
- **影響**:
  - 新規メンバーが混乱する
  - ドキュメントとコードの不一致

### 3. **重複・不要なディレクトリ**
- `script/` と `scripts/` の両方が存在 ⚠️
- `sample/` が空 ⚠️
- `specific/` の用途が不明確

### 4. **スケーラビリティの問題**
- トップレベルに**18個**のディレクトリ → 多すぎる
- 新しい解析タイプを追加しにくい
- 一貫性のあるルールがない

### 5. **一貫性の欠如**
- `azim_mean/` はサブディレクトリで整理 ✓ 良い例
- `3d/`, `2d/` はフラット構造
- 整理の基準がディレクトリごとに異なる

---

## 💡 改善案（3パターン）

### 【パターンA】機能別分離（calc/plot 分離）

データ処理と可視化を明確に分離する構成。

```
tc_analyze/
├── analysis/              # データ処理（calc）
│   ├── spatial/
│   │   ├── 2d/
│   │   └── 3d/
│   ├── azimuthal/
│   │   ├── basic/
│   │   ├── eliassen/
│   │   ├── momentum_u/
│   │   ├── momentum_w/
│   │   └── q8/
│   ├── vertical/
│   │   ├── profile/
│   │   └── profile_q4/
│   ├── center/
│   ├── sums/
│   └── symmetrisity/
│
├── visualization/         # 可視化（plot）
│   ├── spatial/
│   │   ├── 2d/
│   │   └── 3d/
│   ├── azimuthal/
│   │   ├── basic/
│   │   ├── eliassen/
│   │   ├── momentum_u/
│   │   ├── momentum_w/
│   │   └── q8/
│   ├── vertical/
│   │   ├── profile/
│   │   └── profile_q4/
│   ├── center/
│   ├── sums/
│   └── symmetrisity/
│
├── utils/                 # 共通モジュール（変更なし）
├── scripts/               # 実行スクリプト（統合）
├── data_processing/       # データ前処理
└── docs/                  # ドキュメント
```

**メリット**:
- ✅ データフローが明確（analysis → data → visualization）
- ✅ calc/plot の責任分離
- ✅ 同じ解析の calc と plot が対応関係が明確

**デメリット**:
- ❌ ディレクトリ階層が深くなる
- ❌ 関連ファイル（calc + plot）が物理的に離れる
- ❌ 既存スクリプトの大規模な移動が必要

**移行コスト**: 🔴 **高** (全ファイル移動、analyze.sh大幅変更)

---

### 【パターンB】解析タイプ別 + サブディレクトリ（推奨）

現在の構造を活かしつつ、各解析タイプ内で calc/plot を整理。

```
tc_analyze/
├── analysis/
│   ├── spatial/
│   │   ├── 2d/
│   │   │   ├── calc/
│   │   │   ├── plot/
│   │   │   └── README.md
│   │   └── 3d/
│   │       ├── calc/
│   │       ├── plot/
│   │       └── README.md
│   │
│   ├── azimuthal/         # azim_mean → azimuthal に改名
│   │   ├── basic/
│   │   │   ├── calc/
│   │   │   └── plot/
│   │   ├── eliassen/
│   │   │   ├── calc/
│   │   │   └── plot/
│   │   ├── momentum/
│   │   │   ├── u/
│   │   │   │   ├── calc/
│   │   │   │   └── plot/
│   │   │   └── w/
│   │   │       ├── calc/
│   │   │       └── plot/
│   │   ├── q8/            # azim_q8 → azimuthal/q8
│   │   │   ├── calc/
│   │   │   └── plot/
│   │   └── README.md
│   │
│   ├── vertical/
│   │   ├── profile/       # z_profile
│   │   │   ├── calc/
│   │   │   └── plot/
│   │   └── q4/            # z_profile_q4
│   │       ├── calc/
│   │       └── plot/
│   │
│   ├── center/
│   │   ├── calc/
│   │   └── plot/
│   │
│   ├── diagnostics/       # sums, symmetrisity
│   │   ├── sums/
│   │   │   ├── calc/
│   │   │   └── plot/
│   │   └── symmetrisity/
│   │       ├── calc/
│   │       └── plot/
│   │
│   └── README.md
│
├── utils/                 # 共通モジュール（変更なし）
├── scripts/               # 実行スクリプト（script + scriptsを統合）
├── data_processing/       # データ前処理
├── docs/                  # ドキュメント（既存MDファイル）
└── archive/               # 旧ファイル保管

不要ディレクトリ削除:
  - sample/ → 削除
  - specific/ → examples/ または archive/ に統合
  - examples/ → archive/ に移動（または独立保持）
```

**メリット**:
- ✅ 解析タイプごとに整理され、見通しが良い
- ✅ calc/plot の分離で役割が明確
- ✅ azim_mean の良い構造を全体に適用
- ✅ カテゴリ名とディレクトリ名の一致を改善
- ✅ 中程度の移行コスト

**デメリット**:
- △ 一部のディレクトリは階層が深い（azimuthal/momentum/u/calc）

**移行コスト**: 🟡 **中** (ディレクトリ移動、analyze.sh一部変更)

---

### 【パターンC】現状維持 + 最小限の改善

現在の構造をほぼ維持し、最小限の変更のみ実施。

```
tc_analyze/
├── 2d/
│   ├── calc/              # 新規: 3 calc.py を移動
│   ├── plot/              # 新規: 6 plot.py を移動
│   └── (他のファイル)
├── 3d/
│   ├── calc/              # 新規: 8 calc.py を移動
│   ├── plot/              # 新規: 20 plot.py を移動
│   └── (他のファイル)
├── azim_mean/
│   ├── calc/              # 新規: 17 calc.py を移動
│   ├── plot/              # 新規: 35 plot.py を移動
│   ├── eliassen/
│   │   ├── calc/          # 既存 calc を移動
│   │   └── plot/          # 既存 plot を移動
│   ├── eq_momentum_u/
│   │   ├── calc/
│   │   └── plot/
│   └── eq_momentum_w/
│       ├── calc/
│       └── plot/
├── azim_q8/
│   ├── calc/
│   └── plot/
├── (その他同様)
├── utils/                 # 変更なし
└── scripts/               # script/ と統合

最小限の変更:
  - script/ と scripts/ を統合
  - sample/ を削除
  - 各ディレクトリ内で calc/ と plot/ に分離
```

**メリット**:
- ✅ 移行コストが最小
- ✅ analyze.sh の変更が少ない
- ✅ 既存の構造に慣れたメンバーの混乱が少ない

**デメリット**:
- ❌ トップレベルディレクトリの多さは解決されない
- ❌ 命名の不一致は残る（azim vs azim_mean）
- ❌ スケーラビリティの問題は残る

**移行コスト**: 🟢 **低** (ディレクトリ内の整理のみ)

---

## 🎯 推奨案: パターンB（解析タイプ別 + サブディレクトリ）

### 推奨理由

1. **バランスが良い**
   - 現状の良い点（azim_mean/ の構造）を活かす
   - 問題点（calc/plot混在、命名不一致）を解決
   - 移行コストが中程度で現実的

2. **将来の拡張性**
   - 新しい解析タイプを追加しやすい
   - 一貫したルールで整理されている

3. **可読性の向上**
   - analysis/ 配下で全体像を把握しやすい
   - calc/plot の分離でデータフローが明確

4. **保守性の向上**
   - 関連ファイルが近くにまとまる
   - ドキュメント（README.md）を各レベルに配置可能

---

## 📋 移行手順（パターンB採用時）

### フェーズ1: 準備（1日）

1. **バックアップ作成**
   ```bash
   git add -A
   git commit -m "Before directory restructure"
   git tag pre-restructure
   ```

2. **新ディレクトリ構造の作成**
   ```bash
   mkdir -p analysis/{spatial/{2d,3d},azimuthal/{basic,eliassen,momentum/{u,w},q8},vertical/{profile,q4},center,diagnostics/{sums,symmetrisity}}
   ```

3. **calc/plot サブディレクトリ作成スクリプト**
   ```bash
   for dir in analysis/spatial/{2d,3d} analysis/azimuthal/{basic,eliassen,momentum/{u,w},q8} analysis/vertical/{profile,q4} analysis/center analysis/diagnostics/{sums,symmetrisity}; do
       mkdir -p "$dir"/{calc,plot}
   done
   ```

### フェーズ2: ファイル移行（2-3日）

1. **2d/ → analysis/spatial/2d/**
   ```bash
   # calcファイル
   mv 2d/*_calc.py analysis/spatial/2d/calc/

   # plotファイル
   mv 2d/*_plot.py analysis/spatial/2d/plot/
   mv 2d/whole_domain.py analysis/spatial/2d/plot/
   mv 2d/vortex_region.py analysis/spatial/2d/plot/

   # シェルスクリプト
   mv 2d/*.sh analysis/spatial/2d/
   ```

2. **3d/ → analysis/spatial/3d/**
   ```bash
   mv 3d/*_calc.py analysis/spatial/3d/calc/
   mv 3d/*_plot.py analysis/spatial/3d/plot/
   mv 3d/*.sh analysis/spatial/3d/
   ```

3. **azim_mean/ → analysis/azimuthal/**
   ```bash
   # basic (直下のファイル)
   mv azim_mean/*_calc.py analysis/azimuthal/basic/calc/
   mv azim_mean/*_plot.py analysis/azimuthal/basic/plot/
   mv azim_mean/*.sh analysis/azimuthal/basic/

   # eliassen
   mv azim_mean/eliassen/*_calc.py analysis/azimuthal/eliassen/calc/
   mv azim_mean/eliassen/*_plot.py analysis/azimuthal/eliassen/plot/

   # momentum_u
   mv azim_mean/eq_momentum_u/*_calc.py analysis/azimuthal/momentum/u/calc/
   mv azim_mean/eq_momentum_u/*_plot.py analysis/azimuthal/momentum/u/plot/

   # momentum_w
   mv azim_mean/eq_momentum_w/*_calc.py analysis/azimuthal/momentum/w/calc/
   mv azim_mean/eq_momentum_w/*_plot.py analysis/azimuthal/momentum/w/plot/
   ```

4. **その他のディレクトリも同様に移行**

### フェーズ3: スクリプト更新（1-2日）

1. **analyze.shの更新**
   - パスの変更（例: `3d/ → analysis/spatial/3d/`）
   - カテゴリ名の統一（例: `azim → azimuthal/basic`）

2. **Pythonスクリプトのインポートパス確認**
   - `utils/` の参照は変更不要（相対パス使用）

### フェーズ4: 検証（1日）

1. **構文チェック**
   ```bash
   python -m py_compile analysis/**/*.py
   ```

2. **テスト実行**
   ```bash
   sh scripts/analyze.sh center --dry-run
   sh scripts/analyze.sh spatial_2d --dry-run
   ```

3. **ドキュメント更新**
   - ARCHITECTURE.md
   - COMMAND_REFERENCE.md
   - README.md

### フェーズ5: クリーンアップ（半日）

1. **旧ディレクトリの削除**
   ```bash
   rm -rf 2d/ 3d/ azim_mean/ azim_q8/ z_profile/ z_profile_q4/ center/ sums/ symmetrisity/
   rm -rf sample/ specific/
   ```

2. **script/ と scripts/ の統合**
   ```bash
   mv script/* scripts/
   rm -rf script/
   ```

**総所要時間**: 約5-7日（検証含む）

---

## 🔄 代替案: 段階的移行

一度に全てを変更するのが難しい場合、段階的に移行：

### ステップ1: calc/plot 分離のみ（パターンC）
- 各ディレクトリ内で calc/ と plot/ に分離
- 最小限の変更で効果を得る

### ステップ2: トップレベルの整理
- analysis/ ディレクトリを新設
- 徐々に移行（spatial → azimuthal → vertical）

### ステップ3: 命名の統一
- カテゴリ名とディレクトリ名を一致させる

---

## ❓ FAQ

### Q1: 既存のデータパス（./data/, ./fig/）は変更される？
**A**: いいえ。ディレクトリ構造の変更はソースコードのみで、データパスは`config.get_data_path()`と`config.get_fig_path()`で管理されているため影響なし。

### Q2: analyze.sh の変更はどの程度必要？
**A**: パターンBの場合、カテゴリ名とパスの対応を更新する必要あり。約50-100行の変更。

### Q3: 移行中に既存の解析を実行できる？
**A**: はい。Git branchを切って移行作業を行い、必要に応じて元のbranchで解析を継続可能。

### Q4: utils/ は移動しなくて良い？
**A**: はい。`pip install -e .`でインストールされているため、どこから参照しても動作します。

---

## 📊 比較表

| 項目 | パターンA | パターンB（推奨） | パターンC |
|------|----------|-----------------|----------|
| calc/plot分離 | ✅ 完全 | ✅ 完全 | ✅ 完全 |
| 階層の深さ | ❌ 深い | 〇 適度 | ✅ 浅い |
| 命名の一貫性 | ✅ 高 | ✅ 高 | ❌ 低 |
| 移行コスト | ❌ 高 | 〇 中 | ✅ 低 |
| 将来の拡張性 | ✅ 高 | ✅ 高 | ❌ 低 |
| **総合評価** | △ | ✅ **推奨** | △ |

---

**最終更新**: 2025-11-27
**バージョン**: 1.0
