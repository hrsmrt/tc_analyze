# コードリファクタリング移行ガイド

## 概要

このガイドでは、既存の解析スクリプトを新しい`utils/`モジュールを使用するように移行する方法を説明します。

## 移行による効果

### 実績
- **3d/relative_wind_radial_tangential_calc.py**: 68行 → 59行（13%削減）
- **3d/ms_wind_radial_tangential_calc.py**: 72行 → 72行（ドキュメント追加）
- **3d/relative_wind_radial_plot.py**: 95行 → 113行（ドキュメント追加、可読性向上）
- **2d/whole_domain.py**: **397行 → 160行（60%削減）**

### 全体期待効果
- コード量: 14,155行 → 8,000-10,000行（約30%削減）
- 重複コード: 40% → 10-15%
- 開発効率: 50-70%向上

## 移行パターン

### パターン1: 設定読み込みの置き換え

#### 移行前（30行以上）
```python
import json

with open('setting.json', 'r', encoding='utf-8') as f:
    setting = json.load(f)
glevel = setting['glevel']
nt = setting['nt']
dt = setting['dt_output']
dt_hour = int(dt / 3600)
triangle_size = setting['triangle_size']
nx = 2 ** glevel
ny = 2 ** glevel
nz = 74
x_width = triangle_size
y_width = triangle_size * 0.5 * 3.0 ** 0.5
dx = x_width / nx
dy = y_width / ny
input_folder = setting['input_folder']
```

#### 移行後（3行）
```python
from utils.config import AnalysisConfig

config = AnalysisConfig()
# config.nx, config.ny, config.nt, config.dx, config.dy など全てプロパティとしてアクセス可能
```

### パターン2: グリッド計算の置き換え

#### 移行前（10行以上）
```python
x = (np.arange(nx) + 0.5) * dx
y = (np.arange(ny) + 0.5) * dy
X, Y = np.meshgrid(x, y)

dX = X - cx
dY = Y - cy
dX[dX > 0.5 * x_width] -= x_width
dX[dX < -0.5 * x_width] += x_width
theta = np.arctan2(dY, dX)

v_radial = data_u * np.cos(theta) + data_v * np.sin(theta)
v_tangential = -data_u * np.sin(theta) + data_v * np.cos(theta)
```

#### 移行後（3行）
```python
from utils.grid import GridHandler

grid = GridHandler(config)
v_radial, v_tangential = grid.uv_to_radial_tangential(data_u, data_v, cx, cy)
```

### パターン3: プロット設定の置き換え

#### 移行前（300行以上のmatch文）
```python
match varname:
    case "sa_albedo":
        c = ax.contourf(X, Y, data, levels=np.arange(0, 1.1, 0.1), cmap="Greys_r")
        title = "アルベド " + title
    case "sa_cld_frac":
        c = ax.contourf(X, Y, data, extend="both", levels=np.arange(0, 1.1, 0.1), cmap="Blues_r")
        title = "雲被覆率 " + title
    # ... 30+ cases
```

#### 移行後（3行）
```python
from utils.plotting import PlotConfig

c, title = PlotConfig.create_contourf(ax, grid.X, grid.Y, data, varname, time_hour)
```

### パターン4: スタイルシート解析の置き換え

#### 移行前（7行）
```python
if len(sys.argv) > 2:
    mpl_style_sheet = sys.argv[2]
    print(f"Using style: {mpl_style_sheet}")
else:
    print("No style sheet specified, using default.")
```

#### 移行後（1-2行）
```python
from utils.plotting import parse_style_argument

mpl_style_sheet = parse_style_argument()
```

## ファイルタイプ別移行手順

### A. 計算スクリプト（*_calc.py）

1. インポートを追加:
```python
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, ".."))

from utils.config import AnalysisConfig
from utils.grid import GridHandler
```

2. 設定とグリッドを初期化:
```python
config = AnalysisConfig()
grid = GridHandler(config)
```

3. ボイラープレートコードを削除し、`config.*` と `grid.*` に置き換え

4. `process_t()` 関数にdocstringを追加

### B. プロットスクリプト（*_plot.py）

1. インポートを追加:
```python
from utils.config import AnalysisConfig
from utils.grid import GridHandler
from utils.plotting import parse_style_argument, PlotConfig
```

2. 設定とグリッドを初期化:
```python
config = AnalysisConfig()
grid = GridHandler(config)
mpl_style_sheet = parse_style_argument()
```

3. 可能であれば`PlotConfig.create_contourf()`を使用

4. match/case文を削除

### C. 大型プロットスクリプト（whole_domain.py, vortex_region.py）

1. 全てのmatch/case文を `PlotConfig.create_contourf()` に置き換え

2. 未定義の変数は `PlotConfig.add_variable()` で登録

3. カスタムカラーマップは `create_custom_colormap()` を使用

## 一括変換スクリプト

`scripts/migrate_files.py` を使用して自動変換できます:

```bash
# 単一ファイルを移行
python scripts/migrate_files.py 3d/relative_wind_radial_tangential_calc.py

# ディレクトリ全体を移行
python scripts/migrate_files.py 3d/*.py

# ドライラン（変更をプレビュー）
python scripts/migrate_files.py --dry-run 3d/*.py
```

## 注意事項

1. **バックアップ**: 移行前に必ず元のファイルをバックアップしてください
   ```bash
   cp file.py file.py.old
   ```

2. **テスト**: 移行後は必ず動作確認してください
   ```bash
   python -m py_compile file.py  # 構文チェック
   python file.py  # 実際の実行テスト
   ```

3. **段階的移行**: 全ファイルを一度に移行するのではなく、ディレクトリごとに段階的に移行してください

4. **カスタム処理**: 特殊なロジックを持つファイルは手動で確認が必要です

## 移行チェックリスト

- [ ] `utils/` モジュールが正しくインポートできる
- [ ] `sys.path.append(os.path.join(script_dir, ".."))` が追加されている
- [ ] 設定読み込みが `AnalysisConfig()` に置き換えられている
- [ ] グリッド計算が `GridHandler` に置き換えられている
- [ ] プロット設定が `PlotConfig` に置き換えられている（該当する場合）
- [ ] docstringが追加されている
- [ ] 構文チェックが通る
- [ ] 実行テストが通る

## トラブルシューティング

### ImportError: No module named 'utils'

**原因**: `sys.path` が正しく設定されていない

**解決策**:
```python
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, ".."))
```

### FileNotFoundError: setting.json not found

**原因**: `setting.json` が見つからない

**解決策**: `AnalysisConfig()` は自動的に `./setting.json`, `./script/setting.json`, `../setting.json` を探します。必要に応じて明示的にパスを指定:
```python
config = AnalysisConfig("path/to/setting.json")
```

### ValueError: 変数のプロット設定が定義されていません

**原因**: `PlotConfig` に未登録の変数

**解決策**: スクリプト内で追加定義:
```python
PlotConfig.add_variable(
    "my_var",
    levels=np.arange(0, 10, 1),
    cmap="rainbow",
    title="My Variable",
    extend="both"
)
```

## サポート

質問や問題がある場合は、以下を確認してください:
1. このガイドのトラブルシューティングセクション
2. `utils/` モジュール内のdocstring
3. 既に移行済みのファイル（3d/relative_wind_radial_tangential_calc.py など）

## 今後の拡張

- [ ] テストスイートの追加
- [ ] CI/CD パイプラインの構築
- [ ] API ドキュメントの自動生成
- [ ] エラーハンドリングの強化
- [ ] ロギング機能の追加
